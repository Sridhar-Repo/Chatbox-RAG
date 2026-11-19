import type { Source } from "../types";

interface Props {
  sources: Source[];
  open: Set<number>;
  onToggle: (n: number, isOpen: boolean) => void;
}

export function SourceList({ sources, open, onToggle }: Props) {
  return (
    <div className="sources">
      {sources.map((s) => (
        <details
          key={s.n}
          className="src"
          open={open.has(s.n)}
          onToggle={(e) => onToggle(s.n, e.currentTarget.open)}
        >
          <summary>
            <span className="n">{s.n}</span>
            <span className="where">
              {s.source}
              {s.page ? `, page ${s.page}` : ""}
            </span>
            <span className="score">{Math.round(s.score * 100)}% match</span>
          </summary>
          <pre>{s.text}</pre>
        </details>
      ))}
    </div>
  );
}
