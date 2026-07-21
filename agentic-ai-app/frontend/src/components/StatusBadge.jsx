export default function StatusBadge({ health, error }) {
  if (error) {
    return (
      <div className="flex items-center gap-2 rounded-full border border-blueprint-rose/40 bg-blueprint-rose/10 px-3 py-1 text-xs font-mono text-blueprint-rose">
        <span className="h-1.5 w-1.5 rounded-full bg-blueprint-rose" />
        BACKEND OFFLINE
      </div>
    );
  }
  if (!health) {
    return (
      <div className="flex items-center gap-2 rounded-full border border-blueprint-line px-3 py-1 text-xs font-mono text-blueprint-muted">
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-blueprint-muted" />
        CONNECTING…
      </div>
    );
  }
  const live = !health.mock_mode;
  return (
    <div
      className={`flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-mono ${
        live
          ? "border-blueprint-cyan/40 bg-blueprint-cyan/10 text-blueprint-cyan"
          : "border-blueprint-amber/40 bg-blueprint-amber/10 text-blueprint-amber"
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${live ? "bg-blueprint-cyan" : "bg-blueprint-amber"}`} />
      {live ? `LIVE · ${health.model}` : "MOCK MODE · no API key set"}
    </div>
  );
}
