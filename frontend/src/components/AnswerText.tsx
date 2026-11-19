interface Props {
  text: string;
  validCitations: Set<number>;
  onCite: (n: number) => void;
}

/** Renders the answer as plain text (React escapes it) and turns [n] into clickable badges. */
export function AnswerText({ text, validCitations, onCite }: Props) {
  const parts = text.split(/\[(\d+)\]/); // odd positions are the citation numbers
  return (
    <>
      {parts.map((part, i) => {
        if (i % 2 === 0) return part;
        const n = Number(part);
        return validCitations.has(n) ? (
          <button key={i} type="button" className="cite" onClick={() => onCite(n)}>
            {n}
          </button>
        ) : (
          `[${part}]`
        );
      })}
    </>
  );
}
