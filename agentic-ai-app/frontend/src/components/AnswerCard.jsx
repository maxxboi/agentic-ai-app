const CONFIDENCE_META = {
  high: { color: "text-blueprint-cyan", border: "border-blueprint-cyan/50" },
  medium: { color: "text-blueprint-amber", border: "border-blueprint-amber/50" },
  low: { color: "text-blueprint-rose", border: "border-blueprint-rose/50" },
};

export default function AnswerCard({ answer, onFollowUp }) {
  const meta = CONFIDENCE_META[answer.confidence] || CONFIDENCE_META.medium;

  return (
    <div className="relative rounded-xl border border-blueprint-line bg-blueprint-panel p-6">
      {/* Signature element: schema-validated approval stamp */}
      <div
        className={`absolute -right-3 -top-3 flex h-16 w-16 rotate-6 select-none items-center justify-center rounded-full border-2 border-dashed ${meta.border} bg-blueprint-panel font-mono text-[9px] leading-tight ${meta.color}`}
        title="This answer passed Pydantic schema validation"
      >
        <div className="text-center">
          <div className="text-[13px]">✓</div>
          <div>SCHEMA</div>
          <div>VALID</div>
        </div>
      </div>

      <p className="font-mono text-[11px] tracking-wider text-blueprint-muted">STRUCTURED ANSWER</p>
      <h3 className="mt-2 font-display text-lg font-medium text-blueprint-ink">{answer.summary}</h3>

      {answer.details?.length > 0 && (
        <ul className="mt-4 space-y-2">
          {answer.details.map((d, i) => (
            <li key={i} className="flex gap-2 text-sm text-blueprint-ink/85">
              <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-blueprint-muted" />
              {d}
            </li>
          ))}
        </ul>
      )}

      <div className="mt-5 flex items-center gap-2 font-mono text-[11px]">
        <span className="text-blueprint-muted">CONFIDENCE</span>
        <span className={`rounded border px-1.5 py-0.5 ${meta.border} ${meta.color}`}>
          {answer.confidence.toUpperCase()}
        </span>
      </div>

      {answer.follow_up_questions?.length > 0 && (
        <div className="mt-5 flex flex-wrap gap-2 border-t border-blueprint-line pt-4">
          {answer.follow_up_questions.map((q, i) => (
            <button
              key={i}
              onClick={() => onFollowUp(q)}
              className="rounded-full border border-blueprint-line px-3 py-1 text-xs text-blueprint-muted transition hover:border-blueprint-cyan/50 hover:text-blueprint-cyan"
            >
              {q}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
