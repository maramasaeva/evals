"""Module 4 — metrics, groups, epochs. A metric turns a column of Scores into one number.

run:  uv run inspect eval learn/examples/m4_metrics.py@<task> --model google/gemini-flash-latest --epochs 3
"""
from inspect_ai import Epochs, Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import (
    CORRECT, INCORRECT, Metric, SampleScore, Score, Target, accuracy, grouped, includes,
    mean, metric, scorer, stderr, value_to_float,
)
from inspect_ai.solver import TaskState, generate

DS = [
    Sample(input="What is 7 * 8? Just the number.", target="56", metadata={"hard": False}),
    Sample(input="What is 17 * 23? Just the number.", target="391", metadata={"hard": True}),
    Sample(input="What is 2 ** 10? Just the number.", target="1024", metadata={"hard": False}),
    Sample(input="What is 123 * 45? Just the number.", target="5535", metadata={"hard": True}),
]

# 1. default metrics on includes(): accuracy + stderr. nothing to write.
@task
def defaults():
    return Task(dataset=DS, solver=[generate()], scorer=includes())


# 2. your own metric. receives every SampleScore, returns a float.
#    here: the fraction of answers that were *long* (a proxy for "the model explained itself").
@metric
def frac_verbose() -> Metric:
    def compute(scores: list[SampleScore]) -> float:
        verbose = [s for s in scores if len(str(s.score.answer or "").split()) > 3]
        return len(verbose) / len(scores) if scores else 0.0
    return compute

@scorer(metrics=[accuracy(), stderr(), frac_verbose()])
def includes_plus():
    async def score(state: TaskState, target: Target) -> Score:
        got = state.output.completion
        return Score(value=CORRECT if target.text in got else INCORRECT, answer=got)
    return score

@task
def custom_metric():
    return Task(dataset=DS, solver=[generate()], scorer=includes_plus())


# 3. grouped(): compute a metric per value of a metadata key, plus the overall.
#    this is how the study gets "accuracy per condition" and "stance per pressure" for free.
@task
def by_group():
    return Task(dataset=DS, solver=[generate()],
                scorer=includes(), metrics=[grouped(accuracy(), "hard"), stderr()])


# 4. epochs + reducer. with --epochs 3 every sample runs 3x; the reducer collapses 3 scores to 1
#    BEFORE metrics run. "mean" (default) gives per-sample pass rate; "at_least_1" is pass@3-ish;
#    "mode" is majority vote. try each and watch accuracy move.
@task
def epochs_mean():
    return Task(dataset=DS, solver=[generate()], scorer=includes(), epochs=Epochs(3, "mean"))

@task
def epochs_any():
    return Task(dataset=DS, solver=[generate()], scorer=includes(), epochs=Epochs(3, "at_least_1"))

@task
def epochs_vote():
    return Task(dataset=DS, solver=[generate()], scorer=includes(), epochs=Epochs(3, "mode"))
