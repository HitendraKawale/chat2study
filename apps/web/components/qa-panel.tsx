"use client";

import { useState } from "react";

import { askChat, searchChat } from "@/lib/api";
import type { AskChatResponse, SearchChunksResponse } from "@/types/api";

type Props = {
  chatId: string;
};

export function QAPanel({ chatId }: Props) {
  const [searchQuery, setSearchQuery] = useState("");
  const [question, setQuestion] = useState("");
  const [searchResult, setSearchResult] = useState<SearchChunksResponse | null>(null);
  const [answerResult, setAnswerResult] = useState<AskChatResponse | null>(null);
  const [busy, setBusy] = useState<"search" | "ask" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch() {
    setBusy("search");
    setError(null);
    setAnswerResult(null);

    try {
      const result = await searchChat(chatId, searchQuery, 5);
      setSearchResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setBusy(null);
    }
  }

  async function handleAsk() {
    setBusy("ask");
    setError(null);

    try {
      const result = await askChat(chatId, question, 5);
      setAnswerResult(result);
      setSearchResult({
        chat_id: result.chat_id,
        query: result.question,
        top_k: result.matches.length,
        matches: result.matches,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Question answering failed");
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="text-xl font-semibold text-slate-100">Search chunks</h2>
        <p className="mt-1 text-sm text-slate-400">
          Run semantic retrieval against the indexed chat.
        </p>

        <div className="mt-4 flex flex-col gap-3">
          <input
            type="text"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search for architecture decisions, RAG, embeddings..."
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:border-slate-500 outline-none"
          />
          <button
            type="button"
            onClick={handleSearch}
            disabled={!searchQuery.trim() || busy !== null}
            className="w-fit rounded-xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-100 hover:border-slate-500 disabled:opacity-60"
          >
            {busy === "search" ? "Searching..." : "Search"}
          </button>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="text-xl font-semibold text-slate-100">Ask the chat</h2>
        <p className="mt-1 text-sm text-slate-400">
          Grounded Q&A using retrieval plus your configured LLM backend.
        </p>

        <div className="mt-4 flex flex-col gap-3">
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Summarize the main technical decisions in this chat."
            rows={4}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:border-slate-500 outline-none"
          />
          <button
            type="button"
            onClick={handleAsk}
            disabled={!question.trim() || busy !== null}
            className="w-fit rounded-xl bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-white disabled:opacity-60"
          >
            {busy === "ask" ? "Asking..." : "Ask"}
          </button>
        </div>
      </div>

      {error ? (
        <div className="rounded-2xl border border-red-900 bg-red-950/50 p-4 text-sm text-red-200">
          {error}
        </div>
      ) : null}

      {answerResult ? (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex flex-wrap gap-3 text-xs text-slate-500">
            <span>Provider: {answerResult.model_provider}</span>
            <span>Model: {answerResult.model_name}</span>
          </div>
          <h3 className="mt-3 text-lg font-semibold text-slate-100">Answer</h3>
          <pre className="mt-3 whitespace-pre-wrap rounded-2xl border border-slate-800 bg-slate-950/60 p-4 text-sm leading-6 text-slate-200">
            {answerResult.answer}
          </pre>
        </div>
      ) : null}

      {searchResult ? (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h3 className="text-lg font-semibold text-slate-100">Retrieved chunks</h3>
          <div className="mt-4 space-y-3">
            {searchResult.matches.map((match) => (
              <div
                key={match.chunk_id}
                className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4"
              >
                <div className="flex flex-wrap gap-3 text-xs text-slate-500">
                  <span>Ordinal: {match.ordinal}</span>
                  <span>Distance: {match.distance.toFixed(6)}</span>
                  <span>Tokens: {match.token_count}</span>
                </div>
                <pre className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-200">
                  {match.text}
                </pre>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
