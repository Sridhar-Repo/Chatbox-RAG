import { useRef, useState } from "react";
import type { DragEvent, KeyboardEvent } from "react";
import type { DocInfo } from "../types";

interface Props {
  docs: DocInfo[];
  status: string;
  onUpload: (files: File[]) => void;
  onRemove: (name: string) => void;
}

export function DocumentPanel({ docs, status, onUpload, onRemove }: Props) {
  const input = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);

  const pick = () => input.current?.click();
  const onKey = (e: KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      pick();
    }
  };
  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setOver(false);
    onUpload(Array.from(e.dataTransfer.files));
  };

  return (
    <aside className="sidebar">
      <h1>Chat with your docs</h1>
      <p>Add a few files, then ask questions. Answers come only from what you upload.</p>

      <div
        className={`drop${over ? " over" : ""}`}
        role="button"
        tabIndex={0}
        onClick={pick}
        onKeyDown={onKey}
        onDragOver={(e) => {
          e.preventDefault();
          setOver(true);
        }}
        onDragLeave={() => setOver(false)}
        onDrop={onDrop}
      >
        Drop PDF, TXT or MD here, or click to browse
      </div>
      <input
        ref={input}
        type="file"
        accept=".pdf,.txt,.md"
        multiple
        hidden
        onChange={(e) => {
          onUpload(Array.from(e.target.files ?? []));
          e.target.value = ""; // lets the same file be picked again
        }}
      />

      <div className="status" aria-live="polite">
        {status}
      </div>

      <ul className="docs">
        {docs.map((d) => (
          <li key={d.name}>
            <span className="name" title={d.name}>
              {d.name}
            </span>
            <span className="count">{d.chunks} parts</span>
            <button aria-label={`Remove ${d.name}`} onClick={() => onRemove(d.name)}>
              ×
            </button>
          </li>
        ))}
      </ul>
    </aside>
  );
}
