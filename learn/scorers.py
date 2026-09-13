# **Do.** `learn/scorers.py`: strict and lenient by hand. Then
# `learn/parse.py`: a state-machine parser that splits a response into
# `reply` and `notes` given `<agent_notes>` tags. Test it on hand-written edge
# cases (missing notes, unclosed tag, tag mentioned in prose) *before* any
# model output touches it. This file is reused unchanged in module 8.

import re
from pathlib import Path
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import (
    CORRECT, INCORRECT, PARTIAL, Score, Target, accuracy, exact, includes, match,
    mean, model_graded_qa, pattern, scorer, stderr
)
from inspect_ai.solver import TaskState, generate

from dataset import load_yaml

ROOT = Path(__file__).resolve().parents[1]
DS = str(ROOT / "learn" /"questions.yaml")


@scorer(metrics=[accuracy(), stderr()])
def strict():
    async def score(state: TaskState, target: Target) -> Score:
        got = state.output.completion.strip()
        return Score(
            value=CORRECT if got==target.text 
            else INCORRECT, answer=got, explanation=f"expected exactly {target.text!r}")
    return score

@task
def strict_answer():
    return Task(dataset=load_yaml(DS), solver=[generate()], scorer=strict())


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()

@scorer(metrics=[accuracy(), stderr()])
def lenient():
    async def score(state: TaskState, target: Target) -> Score:
        got = state.output.completion
        ok = norm(got) == norm(target.text)
        return Score(value=CORRECT if ok else INCORRECT, answer=got,
                     explanation=f"normalised {norm(got)!r} vs {norm(target.text)!r}")
    return score


@task
def lenient_answer():
    return Task(dataset=load_yaml(DS), solver=[generate()], scorer=lenient())

