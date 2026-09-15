# What was annoying about building this in Inspect

Running log. One line each, added as it happens. Talking points for Neolithic.

## Hit so far (during the learning track)

- Task paths must be relative to cwd; an absolute path errors with "Non-relative patterns are unsupported". Non-obvious error text for a common mistake.
- A provider quota error (Gemini 429) is retried silently. The run sits at 0 samples with no message unless you pass `--display plain`. Looks like a hang.
- `-M responses_api=true` is required for gpt-6-astra and not the default; discovered via a 400.
- Passing `temperature` to Astra is a 400 from the provider, but Inspect surfaces it late (after dataset load), not at config time.
- Score values for CORRECT / INCORRECT are the one-letter strings "C" / "I" in the viewer and dataframes. Opaque until you know.
- A scorer that returns 1-5 with the default `accuracy()` metric reports "accuracy 5.0" without complaint. Metric / value type mismatch is silent.
- `model_graded_qa` explanations bury the judge's reasoning; you have to open each sample in the viewer to read it. No flat export of judge reasoning.
- Reasoning summaries: Astra returns none (encrypted blob, `redacted=True`), gpt-5.4 does. Inspect doesn't warn that the reasoning column will be empty for a given model.

## Hit while building the study

(add here)
- `system_message("{system}")` with no matching metadata key sends the literal string `{system}` to the model. No warning, no error. 15 samples ran and looked plausible before we noticed every condition was identical. Missing template variables should fail loudly.
- Scores with string or dict values (a stance label) can't use any built-in metric; `grouped`, `mean`, `accuracy` all assume numbers. Categorical scorers need `metrics=[]` and a separate analysis step to get a distribution table.
- No built-in metric for judge parse-failure rate. Every model-graded scorer needs it; we stash a `judge_parsed` flag in `Score.metadata` and count it in analysis.
- Grader model is set with `--model-role grader=...` on every run; there's no `.env` default for roles the way `INSPECT_EVAL_MODEL` covers the main model. Easy to forget, and the error when you forget is a role-lookup failure inside the scorer, not at startup.
- Two `grouped()` metrics on one scorer (mean and stderr) collide on names: the second shows up as `none2`, `unmonitored2`, `monitored2` in the terminal summary with no hint which metric it is. Metric names should carry the metric, not a counter.
- Running `inspect` from a background shell without the venv activated fails with "command not found"; there's no `python -m inspect_ai` entry point mentioned in the CLI docs. Minor, but cost a run.
- The two `grouped()` metrics collision (`never2`, `flagged2`) again, now on a 5-condition table, where it is actively confusing: ten unlabeled rows.
- Positive note for balance: writing a multi-turn solver (generate, append a user message, generate again, three times) was straightforward. `state.messages.append(ChatMessageUser(...))` and `await generate(state)` did what they say. The custom-scorer + judge path also reused cleanly across experiments via plain imports.
- Importing shared scorers from a sibling study folder needs a `sys.path.insert`; Inspect has no notion of a project-local package for eval components.
