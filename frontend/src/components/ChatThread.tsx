import { useEffect, useRef } from "react";
import type { Message } from "../types";
import { MessageBubble } from "./MessageBubble";

interface Props {
  messages: Message[];
  hasDocs: boolean;
}

export function ChatThread({ messages, hasDocs }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  return (
    <div className="thread" ref={ref}>
      <div className="col">
        {messages.length === 0 ? (
          <div className="empty">
            <h2>{hasDocs ? "What would you like to know?" : "Start by adding a document"}</h2>
            <p>
              {hasDocs
                ? "Ask in plain language. I'll show which passages I used."
                : "Drop a file on the left, then ask about it."}
            </p>
          </div>
        ) : (
          messages.map((m) => <MessageBubble key={m.id} message={m} />)
        )}
      </div>
    </div>
  );
}
