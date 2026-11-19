import type { ChatEvent, DocInfo, Turn } from "../types";
import { readSSE } from "./sse";

export const errorMessage = (e: unknown): string =>
  e instanceof Error ? e.message : "Something went wrong.";

async function failIfNotOk(res: Response): Promise<void> {
  if (res.ok) return;
  const body = await res.json().catch(() => ({}));
  throw new Error(body.detail ?? `Request failed (${res.status})`);
}

export async function listDocs(): Promise<DocInfo[]> {
  const res = await fetch("/api/docs");
  await failIfNotOk(res);
  return res.json();
}

export async function uploadDoc(file: File): Promise<void> {
  const form = new FormData();
  form.append("file", file);
  await failIfNotOk(await fetch("/api/upload", { method: "POST", body: form }));
}

export async function deleteDoc(name: string): Promise<void> {
  await failIfNotOk(await fetch(`/api/docs/${encodeURIComponent(name)}`, { method: "DELETE" }));
}

export async function* streamChat(question: string, history: Turn[]): AsyncGenerator<ChatEvent> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history }),
  });
  await failIfNotOk(res);
  if (!res.body) throw new Error("The server sent no response body.");
  yield* readSSE<ChatEvent>(res.body);
}
