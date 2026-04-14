#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://127.0.0.1:8000}"
URL="${URL:-https://example.com}"
TITLE="${TITLE:-Metrics Test Chat}"
RUNS="${RUNS:-5}"
SUCCESS_RUNS="${SUCCESS_RUNS:-10}"
SEARCH_QUERY="${SEARCH_QUERY:-What is this chat about?}"
ASK_QUERY="${ASK_QUERY:-Summarize the main technical decisions in this chat.}"
TOP_K="${TOP_K:-5}"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1"
    exit 1
  }
}

need_cmd curl
need_cmd jq
need_cmd python

WORKDIR=".metrics_tmp"
mkdir -p "$WORKDIR"

echo "== Chat2Study Metrics Runner =="
echo "BASE=$BASE"
echo "URL=$URL"
echo "TITLE=$TITLE"
echo "RUNS=$RUNS"
echo "SUCCESS_RUNS=$SUCCESS_RUNS"
echo

create_chat() {
  local title="$1"
  curl -s -X POST "$BASE/api/v1/chats" \
    -H "Content-Type: application/json" \
    -d "{
      \"url\": \"$URL\",
      \"title\": \"$title\",
      \"source_type\": \"web_chat_url\"
    }"
}

measure_single_flow() {
  echo "== Single flow metrics =="

  CHAT_JSON=$(create_chat "$TITLE")
  echo "$CHAT_JSON" | jq .
  CHAT_ID=$(echo "$CHAT_JSON" | jq -r '.id')

  echo
  echo "CHAT_ID=$CHAT_ID"
  echo

  curl -s -o "$WORKDIR/ingest_response.json" -w "ingest_time=%{time_total}\n" \
    -X POST "$BASE/api/v1/chats/$CHAT_ID/ingest"

  cat "$WORKDIR/ingest_response.json" | jq .

  curl -s -o "$WORKDIR/index_response.json" -w "index_time=%{time_total}\n" \
    -X POST "$BASE/api/v1/chats/$CHAT_ID/index"

  cat "$WORKDIR/index_response.json" | jq .

  curl -s -o "$WORKDIR/search_response.json" -w "search_time=%{time_total}\n" \
    -X POST "$BASE/api/v1/chats/$CHAT_ID/search" \
    -H "Content-Type: application/json" \
    -d "{
      \"query\": \"$SEARCH_QUERY\",
      \"top_k\": $TOP_K
    }"

  cat "$WORKDIR/search_response.json" | jq .

  curl -s -o "$WORKDIR/ask_response.json" -w "ask_time=%{time_total}\n" \
    -X POST "$BASE/api/v1/chats/$CHAT_ID/ask" \
    -H "Content-Type: application/json" \
    -d "{
      \"question\": \"$ASK_QUERY\",
      \"top_k\": $TOP_K
    }"

  cat "$WORKDIR/ask_response.json" | jq .

  echo
  echo "== Artifact summary =="
  curl -s "$BASE/api/v1/chats/$CHAT_ID/artifacts" | tee "$WORKDIR/artifacts.json" | jq .

  echo
  echo "artifact_count_total=$(jq 'length' "$WORKDIR/artifacts.json")"
  echo "artifact_count_unique=$(jq '[.[].artifact_type] | unique | length' "$WORKDIR/artifacts.json")"
  echo "chunk_count=$(jq '.chunk_count' "$WORKDIR/index_response.json")"
  echo "embedding_dimensions=$(jq '.embedding_dimensions' "$WORKDIR/index_response.json")"
  echo "model_provider=$(jq -r '.model_provider' "$WORKDIR/ask_response.json")"
  echo "model_name=$(jq -r '.model_name' "$WORKDIR/ask_response.json")"

  export CHAT_ID
}

measure_averages() {
  echo
  echo "== Average ingest time over $RUNS runs =="
  : > "$WORKDIR/ingest_times.txt"
  for i in $(seq 1 "$RUNS"); do
    CHAT_JSON=$(create_chat "Metrics Ingest Run $i")
    CID=$(echo "$CHAT_JSON" | jq -r '.id')
    curl -s -o /dev/null -w "%{time_total}\n" \
      -X POST "$BASE/api/v1/chats/$CID/ingest" | tee -a "$WORKDIR/ingest_times.txt"
  done

  python - <<PY
vals = [float(x.strip()) for x in open("$WORKDIR/ingest_times.txt") if x.strip()]
print({"metric": "ingest_seconds", "runs": len(vals), "min": min(vals), "max": max(vals), "avg": sum(vals)/len(vals)})
PY

  echo
  echo "== Average index time over $RUNS runs =="
  : > "$WORKDIR/index_times.txt"
  for i in $(seq 1 "$RUNS"); do
    CHAT_JSON=$(create_chat "Metrics Index Run $i")
    CID=$(echo "$CHAT_JSON" | jq -r '.id')
    curl -s -X POST "$BASE/api/v1/chats/$CID/ingest" > /dev/null
    curl -s -o /dev/null -w "%{time_total}\n" \
      -X POST "$BASE/api/v1/chats/$CID/index" | tee -a "$WORKDIR/index_times.txt"
  done

  python - <<PY
vals = [float(x.strip()) for x in open("$WORKDIR/index_times.txt") if x.strip()]
print({"metric": "index_seconds", "runs": len(vals), "min": min(vals), "max": max(vals), "avg": sum(vals)/len(vals)})
PY

  echo
  echo "== Average search time over $RUNS runs =="
  : > "$WORKDIR/search_times.txt"
  for i in $(seq 1 "$RUNS"); do
    curl -s -o /dev/null -w "%{time_total}\n" \
      -X POST "$BASE/api/v1/chats/$CHAT_ID/search" \
      -H "Content-Type: application/json" \
      -d "{
        \"query\": \"$SEARCH_QUERY\",
        \"top_k\": $TOP_K
      }" | tee -a "$WORKDIR/search_times.txt"
  done

  python - <<PY
vals = [float(x.strip()) for x in open("$WORKDIR/search_times.txt") if x.strip()]
print({"metric": "search_seconds", "runs": len(vals), "min": min(vals), "max": max(vals), "avg": sum(vals)/len(vals)})
PY

  echo
  echo "== Average ask time over $RUNS runs =="
  : > "$WORKDIR/ask_times.txt"
  for i in $(seq 1 "$RUNS"); do
    curl -s -o /dev/null -w "%{time_total}\n" \
      -X POST "$BASE/api/v1/chats/$CHAT_ID/ask" \
      -H "Content-Type: application/json" \
      -d "{
        \"question\": \"$ASK_QUERY\",
        \"top_k\": $TOP_K
      }" | tee -a "$WORKDIR/ask_times.txt"
  done

  python - <<PY
vals = [float(x.strip()) for x in open("$WORKDIR/ask_times.txt") if x.strip()]
print({"metric": "ask_seconds", "runs": len(vals), "min": min(vals), "max": max(vals), "avg": sum(vals)/len(vals)})
PY
}

measure_success_rate() {
  echo
  echo "== Workflow success rate over $SUCCESS_RUNS runs =="

  success=0
  total="$SUCCESS_RUNS"

  for i in $(seq 1 "$total"); do
    CHAT_JSON=$(create_chat "Success Rate Run $i")
    CID=$(echo "$CHAT_JSON" | jq -r '.id')

    STATUS=$(curl -s -X POST "$BASE/api/v1/chats/$CID/ingest" | jq -r '.job.status')

    if [ "$STATUS" = "completed" ]; then
      success=$((success + 1))
    fi
  done

  python - <<PY
success = $success
total = $total
print({"metric": "workflow_success_rate_percent", "success": success, "total": total, "value": round(success / total * 100, 2)})
PY
}

measure_chunk_counts() {
  echo
  echo "== Average chunk count over $RUNS runs =="
  : > "$WORKDIR/chunk_counts.txt"

  for i in $(seq 1 "$RUNS"); do
    CHAT_JSON=$(create_chat "Chunk Count Run $i")
    CID=$(echo "$CHAT_JSON" | jq -r '.id')
    curl -s -X POST "$BASE/api/v1/chats/$CID/ingest" > /dev/null
    curl -s -X POST "$BASE/api/v1/chats/$CID/index" | jq '.chunk_count' | tee -a "$WORKDIR/chunk_counts.txt"
  done

  python - <<PY
vals = [int(x.strip()) for x in open("$WORKDIR/chunk_counts.txt") if x.strip()]
print({"metric": "chunk_count", "runs": len(vals), "min": min(vals), "max": max(vals), "avg": sum(vals)/len(vals)})
PY
}

summary() {
  echo
  echo "== Resume-friendly summary =="

  python - <<PY
import json

def load_float_list(path):
    return [float(x.strip()) for x in open(path) if x.strip()]

def load_int_list(path):
    return [int(x.strip()) for x in open(path) if x.strip()]

ingest = load_float_list("$WORKDIR/ingest_times.txt")
index = load_float_list("$WORKDIR/index_times.txt")
search = load_float_list("$WORKDIR/search_times.txt")
ask = load_float_list("$WORKDIR/ask_times.txt")
chunks = load_int_list("$WORKDIR/chunk_counts.txt")

artifact_json = json.load(open("$WORKDIR/artifacts.json"))
artifact_types = sorted(set(item["artifact_type"] for item in artifact_json))
index_json = json.load(open("$WORKDIR/index_response.json"))
ask_json = json.load(open("$WORKDIR/ask_response.json"))

summary = {
    "avg_ingest_seconds": round(sum(ingest) / len(ingest), 3),
    "avg_index_seconds": round(sum(index) / len(index), 3),
    "avg_search_seconds": round(sum(search) / len(search), 3),
    "avg_ask_seconds": round(sum(ask) / len(ask), 3),
    "avg_chunk_count": round(sum(chunks) / len(chunks), 2),
    "embedding_dimensions": index_json["embedding_dimensions"],
    "embedding_provider": index_json["embedding_provider"],
    "embedding_model": index_json["embedding_model"],
    "chat_model_provider": ask_json["model_provider"],
    "chat_model_name": ask_json["model_name"],
    "unique_artifact_types": artifact_types,
    "unique_artifact_type_count": len(artifact_types),
}
print(json.dumps(summary, indent=2))
PY
}

measure_single_flow
measure_averages
measure_success_rate
measure_chunk_counts
summary

echo
echo "Done. Temporary outputs saved in $WORKDIR"
