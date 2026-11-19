import { useEffect, useRef, useState } from "react";

interface Props {
  disabled: boolean;
  onSubmit: (question: string) => void;
}

export function Composer({ disabled, onSubmit }: Props) {
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${el.scrollHeight}px`;
    }
  }, [value]);

  const submit = () => {
    const question = value.trim();
    if (!question || disabled) return;
    setValue("");
    onSubmit(question);
  };

  return (
    <form
      className="composer"
      onSubmit={(e) => {
        e.preventDefault();
        submit();
      }}
    >
      <div className="row">
        <textarea
          ref={ref}
          rows={1}
          maxLength={1000}
          value={value}
          aria-label="Your question"
          placeholder="Ask about your documents…"
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
        />
        <button className="send" type="submit" disabled={disabled}>
          Ask
        </button>
      </div>
    </form>
  );
}
