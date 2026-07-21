const KIND_META = {
  thought: { label: "THOUGHT", color: "text-blueprint-muted", dot: "bg-blueprint-muted" },
  tool_call: { label: "TOOL CALL", color: "text-blueprint-amber", dot: "bg-blueprint-amber" },
  tool_result: { label: "TOOL RESULT", color: "text-blueprint-cyan", dot: "bg-blueprint-cyan" },
  final_answer: { label: "FINAL ANSWER", color: "text-blueprint-ink", dot: "bg-blueprint-ink" },
};

export default function TraceStep({ step, index }) {
  const meta = KIND_META[step.type] || KIND_META.thought;
  return (
    <div className="relative pl-8">
      <span className="absolute left-[7px] top-1.5 h-2 w-2 rounded-full ring-4 ring-blueprint-panel" style={{ background: "currentColor" }} />
      <div className={`absolute left-0 top-0 h-full w-px bg-blueprint-line`} />
      <div className="mb-4">
        <div className={`flex items-center gap-2 font-mono text-[11px] tracking-wider ${meta.color}`}>
          <span>{String(index + 1).padStart(2, "0")}</span>
          <span>{meta.label}</span>
        </div>
        <p className="mt-1 text-sm text-blueprint-ink/90">{step.content}</p>
        {step.tool_call && (
          <pre className="mt-2 overflow-x-auto rounded-md border border-blueprint-line bg-blueprint-bg/60 p-2 font-mono text-[11px] text-blueprint-amber">
{`${step.tool_call.name}(${JSON.stringify(step.tool_call.arguments)})`}
          </pre>
        )}
        {step.tool_result !== null && step.tool_result !== undefined && (
          <pre className="mt-2 overflow-x-auto rounded-md border border-blueprint-line bg-blueprint-bg/60 p-2 font-mono text-[11px] text-blueprint-cyan">
{JSON.stringify(step.tool_result, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
