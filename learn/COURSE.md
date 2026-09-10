# Inspect, as a course

Seven modules. Each one: **the idea** (how to think about it), **examples** (a
runnable file in `learn/examples/`, several variants per concept, read them
and run them), **do** (the thing you write by hand), **check** (what to look
for in the log before moving on). One running example threads through:
grading a model on short factual questions. The study in
`study/unmonitored/` is module 8.

Run any example task with

```
uv run inspect eval learn/examples/<file>.py@<task> --model openai/gpt-6-astra -M responses_api=true
```

Add `--display plain` to see HTTP retries. **If a run sits at 0 samples, it
is not hung: the provider is rate-limiting and Inspect is retrying quietly.**
Gemini's free tier ran out on 2026-09-10 after ~30 small runs; Astra costs
cents for these examples and has no such limit.

---

## Module 1 · Datasets and Samples

**Idea.** A `Sample` is one exam question: `input`, `target`, an `id`, and a
`metadata` dict for anything you will want to slice by later. A dataset is a
list of them. Every loader (yaml, json, csv, HuggingFace) ends up producing
that same list, so if you can write the loop yourself, you understand all of
them.

**Examples** `m1_datasets.py` — six tasks over the same idea:
`inline` (a python list), `from_yaml` (the hand-written loop),
`from_json` (a `FieldSpec` renames columns), `from_json_fn` (a function when
the mapping needs logic), `filtered` (`MemoryDataset.filter`),
`mcq` (`choices` + `multiple_choice()` + `choice()`).

**Do.** `learn/dataset.py`: read `learn/questions.yaml` into Samples with a
plain loop. Put `hard` in metadata. Run it.

**Check.** In `inspect view`, every sample shows your `id`, and the metadata
panel shows `hard`. If ids are missing, later analysis gets harder.

## Module 2 · Solvers and TaskState

**Idea.** A solver is a function: state in, changed state out. The
`TaskState` is the conversation so far (`state.messages`), the model's latest
reply (`state.output.completion`), plus `target`, `metadata`, and a `store`
for your own scratch values. `generate()` is the solver that calls the
model. Everything else arranges what the model sees before or after.

**Examples** `m2_solvers.py`: `builtins` (system_message → prompt_template →
generate, in order), `cot` (chain_of_thought is just a template; look at it
in the log), `custom_solver` (edit `state.messages`), `two_calls` (call the
model twice in one solver and write to `state.store`), `critique`
(the built-in answer-critique-revise), `peek` (print the state's fields).

**Do.** `learn/solvers.py`: a `persona(text)` solver, then a solver that
answers, asks the model to reconsider, answers again, and records in
`state.metadata` whether the answer changed.

**Check.** Two assistant messages per sample in the transcript. The
`changed` flag in metadata matches what you see.

## Module 3 · Scorers

**Idea.** A scorer is a function: `(state, target) -> Score`. The `Score`
has `value` (CORRECT/INCORRECT, a number, or a dict), `answer` (what you
extracted), `explanation` (why), `metadata`. **The scorer is the eval.** A
sloppy scorer measures the scorer. Always fill `explanation`; it is how you
debug in the viewer.

**Examples** `m3_scorers.py`: `builtins` (includes / match / exact / pattern
on the same answers, so you see them disagree), `custom` (strict and
lenient), `numeric` (a float value with `mean()`, plus Score metadata),
`partial` (three-way values), `judge` (`model_graded_qa()` with the default
rubric), `judge_scale` (your own rubric and a `SCORE: n` pattern — the shape
of the study's divergence scorer).

**Do.** `learn/scorers.py`: strict and lenient by hand. Then
`learn/parse.py`: a state-machine parser that splits a response into
`reply` and `notes` given `<agent_notes>` tags. Test it on hand-written edge
cases (missing notes, unclosed tag, tag mentioned in prose) *before* any
model output touches it. This file is reused unchanged in module 8.

**Check.** Read the judge's reasoning for every sample in `judge_scale`. If
you disagree with it twice, the rubric is wrong, not the model.

## Module 4 · Metrics, groups, epochs

**Idea.** A scorer grades one answer; a metric turns the column of grades
into a number (`accuracy`, `mean`, `stderr`). `grouped(metric, "key")`
computes it per value of a metadata key. `--epochs n` runs each sample n
times and a *reducer* collapses the n scores to one before metrics run.

**Examples** `m4_metrics.py`: `defaults`, `custom_metric` (a `@metric` that
counts verbose answers), `by_group` (accuracy per `hard`), `epochs_mean` /
`epochs_any` / `epochs_vote` (same task, three reducers; run with
`--epochs 3` and watch accuracy move).

**Do.** One custom metric of your own choosing on the module 3 task.

**Check.** `by_group` prints `hard=True`, `hard=False`, and `all`. The
study's headline table is this, keyed on `condition`.

## Module 5 · Tasks, arguments, roles, running from python

**Idea.** The model is never inside the task; you choose it at run time.
Task function arguments become `-T name=value` flags. `model_role="grader"`
lets the CLI pick the judge with `--model-role grader=...`. `eval()` from
python does what the CLI does and hands back the log objects, which is how
you run sweeps.

**Examples** `m5_tasks.py`: `parametrised` (the three channel conditions as
a `-T condition=` argument, plus `GenerateConfig`), `roles` (judge chosen on
the command line), and `python learn/examples/m5_tasks.py` (loops over
conditions, prints one line per run).

**Do.** Add `condition` as an argument to your module 3 task.

**Check.** `log.eval.task_args` in the log records the condition you passed.

## Module 6 · Logs and analysis

**Idea.** The `.eval` file holds everything: what ran (`log.eval`), the
metrics (`log.results`), every sample with its messages, scores, metadata
and store (`log.samples`), and a timeline of events including the raw
request sent to the provider. `samples_df(dir)` flattens a whole folder into
pandas; metadata and scores become columns.

**Examples** `m6_logs.py logs/course` walks one log top to bottom, then
loads the directory into dataframes.

**Do.** `learn/readlog.py`: print, for one log, each sample's question, final
answer, score value, and explanation. No viewer.

**Check.** You can find, from python alone, the sample the scorer got wrong
and say why.

## Module 7 · Tools and agents (preview)

**Idea.** A tool is a typed python function; its docstring is the description
the model reads. `use_tools(...)` + `generate()` lets the model call tools in
a loop until it answers. `react(tools=[...])` is a ready-made agent. This is
what turns the study from prompting into the agentic version: a real shared
wiki the agent can read and write.

**Examples** `m7_tools.py`: `with_tool` (an `add` tool), `agent_wiki` (a
shared notes page seeded with one agent's note; read what the model writes
back).

**Do.** Nothing yet. Read the transcripts.

## Module 8 · The study

`study/unmonitored/DESIGN.md`. Every piece maps onto a module:

| piece                              | module |
| ---------------------------------- | ------ |
| scenario × condition → Samples     | 1, 5   |
| condition system prompt + generate | 2      |
| parser, judges, keyword scorer     | 3      |
| per-condition tables, 5 epochs     | 4      |
| sweep over models                  | 5      |
| reading what the models wrote      | 6      |
| the wiki-tool version, later       | 7      |

The rule from the plan doc stands: scorers, dataset construction, and
parsing are yours by keystroke. The example files are for reading and
running, not copying into the study.
