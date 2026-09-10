# Learning Inspect, bottom-up

## 0. Inspect in one page (read this whenever you come back)

**What it is.** Inspect is the UK AI Security Institute's Python framework for
running LLM evaluations. You describe *what to ask*, *how the model should
answer*, and *how to grade it*. Inspect does the rest: calls the model
provider, runs samples in parallel, retries on rate limits, writes a `.eval`
log per run, and gives you a viewer and pandas importers for the results.

**How to think about it.** An eval is an exam. You write the questions,
decide how the student is allowed to answer, and write the marking scheme.
Then you can sit any model down for the same exam and compare grades, and
every answer sheet is kept so you can check the marking. Inspect makes the
exam out of three pluggable parts, and *all three are just Python functions
you can write yourself*:

```
dataset  ->  solver(s)  ->  scorer  ->  metrics
questions    how the        grade       aggregate
             model answers  one answer  over all
```

- **Dataset**: a list of `Sample`s. A `Sample` has `input` (the question),
  `target` (what a right answer looks like), `id`, and `metadata` (anything
  you want to slice results by later). Build it from a list, a json/csv file,
  or a HuggingFace dataset.
- **Solver**: a function that takes a `TaskState` and returns it changed.
  The state holds the conversation so far (`state.messages`), the model's
  latest `state.output`, plus `metadata`, `target`, and a `store` for your
  own scratch data. `generate()` is the solver that actually calls the model.
  `system_message("...")` is a solver that prepends a system prompt. Chain
  them in a list; they run in order. Your own solver (imports for both
  snippets: `from inspect_ai.solver import solver, TaskState, Generate`,
  `from inspect_ai.scorer import scorer, Score, Target, accuracy, stderr, CORRECT, INCORRECT`,
  `from inspect_ai.model import ChatMessageSystem`; a runnable copy is in
  `learn/smoke/primer_check.py`):

  ```python
  @solver
  def persona(text: str):
      async def solve(state: TaskState, generate: Generate) -> TaskState:
          state.messages.insert(0, ChatMessageSystem(content=text))
          return state
      return solve
  ```
- **Scorer**: a function that takes the final `TaskState` and the `Target`
  and returns a `Score`: `value` (`CORRECT`/`INCORRECT`, a number, or a
  dict), `answer` (what it extracted), `explanation` (why), `metadata`.
  Built-ins: `includes()`, `match()`, `exact()`, `pattern()`,
  `model_graded_qa()` (a judge model with a rubric). Your own:

  ```python
  @scorer(metrics=[accuracy(), stderr()])
  def strict():
      async def score(state: TaskState, target: Target) -> Score:
          got = state.output.completion.strip()
          return Score(value=CORRECT if got == target.text else INCORRECT,
                       answer=got, explanation=f"expected {target.text!r}")
      return score
  ```
- **Metrics** turn a column of `Score`s into a number: `accuracy()`,
  `mean()`, `stderr()`. Usually you take the defaults.
- **Task** ties it together. `@task` marks the function the CLI can find:

  ```python
  @task
  def my_eval():
      return Task(dataset=[...], solver=[system_message("..."), generate()],
                  scorer=includes())
  ```

**Running.** The model is *not* part of the task; you pick it on the
command line, which is the whole point (same eval, many models):

```
uv run inspect eval learn/dataset.py --model google/gemini-flash-latest
uv run inspect eval learn/dataset.py --model openai/gpt-6-astra -M responses_api=true
uv run inspect eval task.py --model a,b,c          # several models, one log each
uv run inspect eval task.py --epochs 5             # repeat every sample 5x
uv run inspect eval task.py --limit 3              # first 3 samples only (cheap debugging)
uv run inspect eval task.py -T condition=monitored # pass an argument to the @task function
uv run inspect eval task.py --log-dir logs/pilot   # keep runs organised
```

Provider strings look like `provider/model`. Keys live in `.env` and are
picked up automatically.

**Reading results.** `uv run inspect view` opens the log viewer
(http://127.0.0.1:7575). Click a run -> Samples -> a sample: you see every
message sent, the model's full response, and the scorer's verdict with its
explanation. In Python:

```python
from inspect_ai.log import read_eval_log
log = read_eval_log("logs/pilot/....eval")
log.samples[0].messages, log.samples[0].scores

from inspect_ai.analysis import evals_df, samples_df
samples_df("logs/pilot")   # one row per sample, metadata becomes columns
```

**Rules of thumb.**
1. Never trust the aggregate until you have read ~10 transcripts behind it.
   The 2026-09-10 smoke test already produced a false positive: `includes()`
   marked a wrong answer right because the target word appeared in it.
2. Start with `--limit 2` and a cheap model. Scale up only when the
   transcripts look right.
3. Put anything you will want to slice by (condition, pressure type,
   language) in `Sample.metadata`. It costs nothing and it becomes a
   dataframe column.
4. The scorer is the eval. A sloppy scorer measures the scorer.
5. When something is confusing, `read_eval_log` and print. The log has
   everything, including the raw request sent to the provider.

Docs: https://inspect.aisi.org.uk/ (start with Tasks, Solvers, Scorers,
Datasets). Real evals to read: https://github.com/UKGovernmentBEIS/inspect_evals

---

## 1. The plan

The long version of each step, with several runnable examples per concept,
is `learn/COURSE.md` (modules 1–7 map onto steps 1–5; module 8 is step 6).
This list is the checklist; the course is the reading.

Goal: understand the machine, not ship a paper. The real study (`study/unmonitored/`,
the DseWiki-inspired unmonitored-channel eval) waits until step 6. Every step is one file, runs in under a minute on
`google/gemini-flash-latest` (or `openai/gpt-6-astra -M responses_api=true`),
and ends with you reading the log.

The whole framework is four objects. Everything else is library browsing.

| object      | what it is                                              | you meet it in |
| ----------- | ------------------------------------------------------- | -------------- |
| `Sample`    | one question: input, target, metadata, id               | step 1         |
| `TaskState` | the conversation so far + the sample; solvers mutate it | step 2         |
| `Score`     | value + answer + explanation, produced by a scorer      | step 3         |
| `EvalLog`   | the .eval file: every state, every score, config        | step 4         |

A solver is `async (state, generate) -> state`.
A scorer is `async (state, target) -> Score`.
A Task is dataset + solver list + scorer. That is all `@task` does.

## Steps (tick as you go)

- [ ] 1. dataset.py — read `learn/questions.yaml` into Samples by hand
        (a plain loop, no `json_dataset` helper yet). Run with `generate()` +
        `includes()`. Open `inspect view`, read every sample.
- [ ] 2. solvers.py — write `@solver def persona(text)` that prepends a
        system message, then chain `[persona(...), generate()]`. Diff the
        transcripts against step 1.
- [ ] 3. scorers.py — write `@scorer def strict()` (exact match) and
        `@scorer def lenient()` (normalise case/punctuation) BY HAND. Then run
        the built-in `model_graded_qa()` and read the judge's reasoning in the
        log. This is the braid-rule core.
        3b. parse.py — a state-machine parser that splits a response into
        `<reply>` and `<agent_notes>` parts (see study/unmonitored/DESIGN.md).
        Test it on hand-written edge cases before any model sees it. This
        exact file is reused in step 6.
- [ ] 4. readlog.py — `read_eval_log(path)`, loop samples, print messages and
        scores. No viewer. Demystify the file.
- [ ] 5. matrix — `--epochs 3`, two models in one command, `samples_df()`
        into pandas. Metadata on Samples becomes columns.
- [ ] 6. swap the toy dataset for `study/unmonitored/scenarios.yaml` and build
        the three-condition task. Now it's the real thing and every piece is
        already understood. (`q1/probes.yaml` is parked, not deleted.)

Rule from the plan doc still applies: scorer, dataset construction, and the
judge-output parsing are yours by keystroke. Claude scaffolds and reviews.
