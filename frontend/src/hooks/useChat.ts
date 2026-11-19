import { useCallback, useRef, useState } from "react";
import { errorMessage, streamChat } from "../api/client";
import type { Message, Turn } from "../types";

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [busy, setBusy] = useState(false);
  const nextId = useRef(1);

  const ask = useCallback(
    async (question: string) => {
      // Only finished messages become history; the server keeps no session state.
      const history: Turn[] = messages
        .filter((m) => m.status === "done")
        .map((m) => ({ role: m.role, content: m.content }));

      const botId = nextId.current + 1;
      nextId.current += 2;
      setMessages((prev) => [
        ...prev,
        { id: botId - 1, role: "user", content: question, sources: [], status: "done" },
        { id: botId, role: "assistant", content: "", sources: [], status: "streaming" },
      ]);
      setBusy(true);

      const patch = (fn: (m: Message) => Message) =>
        setMessages((prev) => prev.map((m) => (m.id === botId ? fn(m) : m)));

      try {
        for await (const event of streamChat(question, history)) {
          if (event.type === "sources") patch((m) => ({ ...m, sources: event.data }));
          else if (event.type === "token") patch((m) => ({ ...m, content: m.content + event.data }));
          else if (event.type === "error") patch((m) => ({ ...m, content: event.data, status: "error" }));
        }
        patch((m) => (m.status === "streaming" ? { ...m, status: "done" } : m));
      } catch (e) {
        patch((m) => ({ ...m, content: errorMessage(e), status: "error" }));
      } finally {
        setBusy(false);
      }
    },
    [messages],
  );

  return { messages, busy, ask };
}
