"""Module 6 — reading logs without the viewer. The log has everything; learn its shape once.

run:  uv run python learn/examples/m6_logs.py logs/smoke
"""
import sys
from inspect_ai.analysis import evals_df, messages_df, samples_df
from inspect_ai.log import list_eval_logs, read_eval_log

log_dir = sys.argv[1] if len(sys.argv) > 1 else "logs/smoke"

# 1. one log: header, then samples. EvalLog.eval = what ran; .results = metrics; .samples = the transcripts.
paths = list_eval_logs(log_dir)
log = read_eval_log(paths[-1])
print("task:", log.eval.task, "| model:", log.eval.model, "| status:", log.status)
print("task_args:", log.eval.task_args, "| epochs:", log.eval.config.epochs)
if log.results:
    for s in log.results.scores:
        print("scorer:", s.name, {k: round(v.value, 3) for k, v in s.metrics.items()})

# 2. one sample: messages (what was sent and received), output, scores, metadata, store.
smp = log.samples[0]
print("\nsample", smp.id, "epoch", smp.epoch, "target", smp.target)
for m in smp.messages:
    text = m.text if isinstance(m.content, str) else " ".join(getattr(c, "text", "") or f"<{c.type}>" for c in m.content)
    print(f"  {m.role:9} {text[:120]!r}")
for name, sc in (smp.scores or {}).items():
    print(f"  score[{name}] value={sc.value!r} answer={str(sc.answer)[:40]!r} why={str(sc.explanation)[:60]!r}")
print("  metadata:", smp.metadata, "| store:", dict(smp.store))

# 3. events: the timeline. model events carry the RAW request/response to the provider.
for ev in smp.events:
    if ev.event == "model":
        print("\nraw request keys:", sorted(ev.call.request.keys()) if ev.call else None)
        break

# 4. dataframes over a whole directory. metadata_* and score_* become columns.
runs = evals_df(log_dir)
print("\nevals_df:", runs.shape, list(runs.columns)[:12], "...")
samples = samples_df(log_dir)
print("samples_df:", samples.shape)
print(samples[[c for c in samples.columns if c.startswith(("model", "score_", "metadata_"))]].head())
