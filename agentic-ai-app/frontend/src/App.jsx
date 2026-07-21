import { useEffect, useState } from "react";
import StatusBadge from "./components/StatusBadge.jsx";
import QueryForm from "./components/QueryForm.jsx";
import TraceStep from "./components/TraceStep.jsx";
import AnswerCard from "./components/AnswerCard.jsx";
import { getHealth, queryAgent } from "./api.js";

export default function App() {
  const [health, setHealth] = useState(null);
  const [healthError, setHealthError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [prefill, setPrefill] = useState("");

  useEffect(() => {
    getHealth().then(setHealth).catch((e) => setHealthError(e.message));
  }, []);

  async function handleSubmit(query) {
    setLoading(true);
    setError(null);
    setPrefill("");
    try {
      const res = await queryAgent(query);
      setResult(res);
      setHistory((h) => [{ query, id: res.request_id }, ...h].slice(0, 8));
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-8">
      {/* Header */}
      <header className="mb-8 flex items-center justify-between border-b border-blueprint-line pb-6">
        <div>
          <p className="font-mono text-[11px] tracking-[0.2em] text-blueprint-muted">AGENTIC-01</p>
          <h1 className="font-display text-2xl font-bold text-blueprint-ink">Agentic Ops Console</h1>
          <p className="mt-1 max-w-lg text-sm text-blueprint-muted">
            Prompt-engineered agent · tool-forced structured output · every answer validated against a Pydantic schema before it reaches you.
          </p>
        </div>
        <StatusBadge health={health} error={healthError} />
      </header>

      {/* Query */}
      <section className="mb-8">
        <QueryForm onSubmit={handleSubmit} loading={loading} externalValue={prefill} />
        {history.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {history.map((h) => (
              <button
                key={h.id}
                onClick={() => setPrefill(h.query)}
                className="rounded-full border border-blueprint-line px-3 py-1 font-mono text-[11px] text-blueprint-muted hover:border-blueprint-cyan/50 hover:text-blueprint-cyan"
              >
                {h.query.length > 34 ? h.query.slice(0, 34) + "…" : h.query}
              </button>
            ))}
          </div>
        )}
      </section>

      {error && (
        <div className="mb-6 rounded-lg border border-blueprint-rose/40 bg-blueprint-rose/10 p-4 text-sm text-blueprint-rose">
          {error}
        </div>
      )}

      {/* Main grid: trace + answer */}
      <section className="grid flex-1 grid-cols-1 gap-6 lg:grid-cols-[1.3fr_1fr]">
        <div className="rounded-xl border border-blueprint-line bg-blueprint-panel/60 p-6">
          <p className="mb-5 font-mono text-[11px] tracking-wider text-blueprint-muted">
            AGENT TRACE {result ? `· ${result.steps.length} STEPS` : ""}
          </p>
          {!result && !loading && (
            <p className="text-sm text-blueprint-muted">Run a query to see the agent's reasoning steps, tool calls, and results here.</p>
          )}
          {loading && (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-4 w-full animate-pulse rounded bg-blueprint-line/50" />
              ))}
            </div>
          )}
          {result && (
            <div>
              {result.steps.map((step, i) => (
                <TraceStep key={i} step={step} index={i} />
              ))}
            </div>
          )}
        </div>

        <div>
          {result ? (
            <AnswerCard answer={result.answer} onFollowUp={setPrefill} />
          ) : (
            <div className="flex h-full min-h-[200px] items-center justify-center rounded-xl border border-dashed border-blueprint-line text-sm text-blueprint-muted">
              Structured answer will appear here
            </div>
          )}
        </div>
      </section>

      <footer className="mt-10 border-t border-blueprint-line pt-4 font-mono text-[11px] text-blueprint-muted">
        FastAPI + Pydantic backend · React + Vite + Tailwind frontend
      </footer>
    </div>
  );
}
