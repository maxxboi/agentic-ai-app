import { useState, useEffect } from "react";

export default function QueryForm({ onSubmit, loading, externalValue }) {
  const [value, setValue] = useState("");

  useEffect(() => {
    if (externalValue) setValue(externalValue);
  }, [externalValue]);

  function handleSubmit(e) {
    e.preventDefault();
    if (!value.trim() || loading) return;
    onSubmit(value.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3">
      <div className="relative flex-1">
        <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 font-mono text-blueprint-cyan">
          &gt;
        </span>
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Ask the agent something… e.g. 'What is 42 * (17 - 5)?'"
          className="w-full rounded-lg border border-blueprint-line bg-blueprint-panel py-3 pl-9 pr-4 font-mono text-sm text-blueprint-ink placeholder:text-blueprint-muted focus:border-blueprint-cyan/60"
          disabled={loading}
        />
      </div>
      <button
        type="submit"
        disabled={loading || !value.trim()}
        className="rounded-lg bg-blueprint-cyan px-5 py-3 font-display text-sm font-medium text-blueprint-bg transition disabled:cursor-not-allowed disabled:opacity-40 enabled:hover:bg-blueprint-cyan/90"
      >
        {loading ? "Running…" : "Run agent"}
      </button>
    </form>
  );
}
