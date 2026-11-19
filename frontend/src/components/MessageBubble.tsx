import { useMemo, useState } from "react";
import type { Message } from "../types";
import { AnswerText } from "./AnswerText";
import { SourceList } from "./SourceList";

export function MessageBubble({ message }: { message: Message }) {
  const [open, setOpen] = useState<Set<number>>(new Set());
  const valid = useMemo(() => new Set(message.sources.map((s) => s.n)), [message.sources]);

  if (message.role === "user") return <div className="msg user">{message.content}</div>;

  const toggle = (n: number, isOpen: boolean) =>
    setOpen((prev) => {
      const next = new Set(prev);
      if (isOpen) next.add(n);
      else next.delete(n);
      return next;
    });

  const cls = ["msg bot", message.status === "streaming" && "typing", message.status === "error" && "error"]
    .filter(Boolean)
    .join(" ");

  return (
    <div className="turn">
      <div className={cls}>
        <AnswerText text={message.content} validCitations={valid} onCite={(n) => toggle(n, true)} />
      </div>
      {/* Shown as soon as the sources event arrives, not after the answer finishes. */}
      {message.sources.length > 0 && <SourceList sources={message.sources} open={open} onToggle={toggle} />}
    </div>
  );
}
