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

WORKDIR=".metrics_tmp"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1"
    exit 1
  }
}

need_cmd curl
need_cmd jq
need_cmd python

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

has_detail_error() {
  local file="$1"
  jq -e '.detail' "$file" >/dev/null 2>&1
}

print_metric_stats() {
  local file="$1"
  local metric="$2"

  python - <<PY
vals = []
with open("$file", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            vals.append(float(line))

if not vals:
    print({"metric": "$metric", "runs": 0, "error": "no successful runs"})
else:
    print({
        "metric": "$metric",
        "runs": len(vals),
        "min": min(vals),
        "max": max(vals),
        "avg": sum(vals) / len(vals),
    })
PY
}

print_int_metric_stats() {
  local file="$1"
  local metric="$2"

  python - <<PY
vals = []
with open("$file", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            vals.append(int(line))

if not vals:
    print({"metric": "$metric", "runs": 0, "error": "no successful runs"})
else:
    print({
        "metric": "$metric",
        "runs": len(vals),
        "min": min(vals),
        "max": max(vals),
        "avg": sum(vals) / len(vals),
    })
PY
}

measure_single_flow() {
  echo "== Single flow metrics =="

  CHAT_JSON=$(create_chat "$TITLE")
  echo "$CHAT_JSON" | jq .

  CHAT_ID=$(echo "$CHAT_JSON" | jq -r '.id')
  export CHAT_ID

  echo
  echo "CHAT_ID=$CHAT_ID"
  echo

  curl -s -o "$WORKDIR/ingest_response.json" -w "ingest_time=%{time_total}\n" \
    -X POST "$BASE/api/v1/chats/$CHAT_ID/ingest"

  cat "$WORKDIR/ingest_response.json" | jq .

  if has_detail_error "$WORKDIR/ingest_response.json"; then
    echo
    echo "Ingest failed:"
    cat "$WORKDIR/ingest_response.json" | jq .
    exit 1
  fi

  curl -s -o "$WORKDIR/index_response.json" -w "index_time=%{time_total}\n" \
    -X POST "$BASE/api/v1/chats/$CHAT_ID/index"

  cat "$WORKDIR/index_response.json" | jq .

  if has_detail_error "$WORKDIR/index_response.json"; then
    echo
    echo "Indexing failed:"
    cat "$WORKDIR/index_response.json" | jq .
    exit 1
  fi

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
  echo "artifact_types=$(jq -r '[.[].artifact_type] | unique | join(\", \")' "$WORKDIR/artifacts.json")"
  echo "chunk_count=$(jq '.chunk_count' "$WORKDIR/index_response.json")"
  echo "embedding_provider=$(jq -r '.embedding_provider' "$WORKDIR/index_response.json")"
  echo "embedding_model=$(jq -r '.embedding_model' "$WORKDIR/index_response.json")"
  echo "embedding_dimensions=$(jq '.embedding_dimensions' "$WORKDIR/index_response.json")"
  echo "model_provider=$(jq -r '.model_provider' "$WORKDIR/ask_response.json")"
  echo "model_name=$(jq -r '.model_name' "$WORKDIR/ask_response.json")"
}

measure_averages() {
  echo
  echo "== Average ingest time over $RUNS runs =="
  : >"$WORKDIR/ingest_times.txt"

  for i in $(seq 1 "$RUNS"); do
    CHAT_JSON=$(create_chat "Metrics Ingest Run $i")
    CID=$(echo "$CHAT_JSON" | jq -r '.id')

    RESP_FILE="$WORKDIR/ingest_run_$i.json"
    TIME=$(curl -s -o "$RESP_FILE" -w "%{time_total}" \
      -X POST "$BASE/api/v1/chats/$CID/ingest")

    if has_detail_error "$RESP_FILE"; then
      echo "skip ingest run $i: $(jq -r '.detail' "$RESP_FILE")"
      continue
    fi

    echo "$TIME" | tee -a "$WORKDIR/ingest_times.txt"
  done

  print_metric_stats "$WORKDIR/ingest_times.txt" "ingest_seconds"

  echo
  echo "== Average index time over $RUNS runs =="
  : >"$WORKDIR/index_times.txt"

  for i in $(seq 1 "$RUNS"); do
    CHAT_JSON=$(create_chat "Metrics Index Run $i")
    CID=$(echo "$CHAT_JSON" | jq -r '.id')

    INGEST_FILE="$WORKDIR/index_ingest_run_$i.json"
    curl -s -o "$INGEST_FILE" \
      -X POST "$BASE/api/v1/chats/$CID/ingest" >/dev/null

    if has_detail_error "$INGEST_FILE"; then
      echo "skip index run $i: ingest failed: $(jq -r '.detail' "$INGEST_FILE")"
      continue
    fi

    INDEX_FILE="$WORKDIR/index_run_$i.json"
    TIME=$(curl -s -o "$INDEX_FILE" -w "%{time_total}" \
      -X POST "$BASE/api/v1/chats/$CID/index")

    if has_detail_error "$INDEX_FILE"; then
      echo "skip index run $i: $(jq -r '.detail' "$INDEX_FILE")"
      continue
    fi

    echo "$TIME" | tee -a "$WORKDIR/index_times.txt"
  done

  print_metric_stats "$WORKDIR/index_times.txt" "index_seconds"

  echo
  echo "== Average search time over $RUNS runs =="
  : >"$WORKDIR/search_times.txt"

  for i in $(seq 1 "$RUNS"); do
    TIME=$(curl -s -o /dev/null -w "%{time_total}" \
      -X POST "$BASE/api/v1/chats/$CHAT_ID/search" \
      -H "Content-Type: application/json" \
      -d "{
        \"query\": \"$SEARCH_QUERY\",
        \"top_k\": $TOP_K
      }")
    echo "$TIME" | tee -a "$WORKDIR/search_times.txt"
  done

  print_metric_stats "$WORKDIR/search_times.txt" "search_seconds"

  echo
  echo "== Average ask time over $RUNS runs =="
  : >"$WORKDIR/ask_times.txt"

  for i in $(seq 1 "$RUNS"); do
    TIME=$(curl -s -o /dev/null -w "%{time_total}" \
      -X POST "$BASE/api/v1/chats/$CHAT_ID/ask" \
      -H "Content-Type: application/json" \
      -d "{
        \"question\": \"$ASK_QUERY\",
        \"top_k\": $TOP_K
      }")
    echo "$TIME" | tee -a "$WORKDIR/ask_times.txt"
  done

  print_metric_stats "$WORKDIR/ask_times.txt" "ask_seconds"
}

measure_success_rate() {
  echo
  echo "== Workflow success rate over $SUCCESS_RUNS runs =="

  success=0
  total="$SUCCESS_RUNS"

  for i in $(seq 1 "$total"); do
    CHAT_JSON=$(create_chat "Success Rate Run $i")
    CID=$(echo "$CHAT_JSON" | jq -r '.id')

    RESP_FILE="$WORKDIR/success_run_$i.json"
    curl -s -o "$RESP_FILE" \
      -X POST "$BASE/api/v1/chats/$CID/ingest" >/dev/null

    if has_detail_error "$RESP_FILE"; then
      continue
    fi

    STATUS=$(jq -r '.job.status' "$RESP_FILE")

    if [ "$STATUS" = "completed" ]; then
      success=$((success + 1))
    fi
  done

  python - <<PY
success = $success
total = $total
print({
    "metric": "workflow_success_rate_percent",
    "success": success,
    "total": total,
    "value": round(success / total * 100, 2) if total else 0.0,
})
PY
}

measure_chunk_counts() {
  echo
  echo "== Average chunk count over $RUNS runs =="
  : >"$WORKDIR/chunk_counts.txt"

  for i in $(seq 1 "$RUNS"); do
    CHAT_JSON=$(create_chat "Chunk Count Run $i")
    CID=$(echo "$CHAT_JSON" | jq -r '.id')

    INGEST_FILE="$WORKDIR/chunk_ingest_run_$i.json"
    curl -s -o "$INGEST_FILE" \
      -X POST "$BASE/api/v1/chats/$CID/ingest" >/dev/null

    if has_detail_error "$INGEST_FILE"; then
      echo "skip chunk run $i: ingest failed: $(jq -r '.detail' "$INGEST_FILE")"
      continue
    fi

    INDEX_FILE="$WORKDIR/chunk_run_$i.json"
    curl -s -o "$INDEX_FILE" \
      -X POST "$BASE/api/v1/chats/$CID/index" >/dev/null

    if has_detail_error "$INDEX_FILE"; then
      echo "skip chunk run $i: $(jq -r '.detail' "$INDEX_FILE")"
      continue
    fi

    jq '.chunk_count' "$INDEX_FILE" | tee -a "$WORKDIR/chunk_counts.txt"
  done

  print_int_metric_stats "$WORKDIR/chunk_counts.txt" "chunk_count"
}

summary() {
  echo
  echo "== metrics summary =="

  python - <<PY
import json
from pathlib import Path

workdir = Path("$WORKDIR")

def load_float_list(path):
    if not path.exists():
        return []
    vals = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            vals.append(float(line))
    return vals

def load_int_list(path):
    if not path.exists():
        return []
    vals = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            vals.append(int(line))
    return vals

summary = {}

ingest = load_float_list(workdir / "ingest_times.txt")
index = load_float_list(workdir / "index_times.txt")
search = load_float_list(workdir / "search_times.txt")
ask = load_float_list(workdir / "ask_times.txt")
chunks = load_int_list(workdir / "chunk_counts.txt")

if ingest:
    summary["avg_ingest_seconds"] = round(sum(ingest) / len(ingest), 3)
if index:
    summary["avg_index_seconds"] = round(sum(index) / len(index), 3)
if search:
    summary["avg_search_seconds"] = round(sum(search) / len(search), 3)
if ask:
    summary["avg_ask_seconds"] = round(sum(ask) / len(ask), 3)
if chunks:
    summary["avg_chunk_count"] = round(sum(chunks) / len(chunks), 2)

artifacts_path = workdir / "artifacts.json"
if artifacts_path.exists():
    artifact_json = json.loads(artifacts_path.read_text(encoding="utf-8"))
    artifact_types = sorted(set(item["artifact_type"] for item in artifact_json))
    summary["unique_artifact_types"] = artifact_types
    summary["unique_artifact_type_count"] = len(artifact_types)

index_path = workdir / "index_response.json"
if index_path.exists():
    index_json = json.loads(index_path.read_text(encoding="utf-8"))
    if "embedding_dimensions" in index_json:
        summary["embedding_dimensions"] = index_json["embedding_dimensions"]
    if "embedding_provider" in index_json:
        summary["embedding_provider"] = index_json["embedding_provider"]
    if "embedding_model" in index_json:
        summary["embedding_model"] = index_json["embedding_model"]
    if "chunk_count" in index_json:
        summary["single_run_chunk_count"] = index_json["chunk_count"]

ask_path = workdir / "ask_response.json"
if ask_path.exists():
    ask_json = json.loads(ask_path.read_text(encoding="utf-8"))
    if "model_provider" in ask_json:
        summary["chat_model_provider"] = ask_json["model_provider"]
    if "model_name" in ask_json:
        summary["chat_model_name"] = ask_json["model_name"]

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
