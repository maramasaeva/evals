# **Do.** `learn/scorers.py`: strict and lenient by hand. Then
# `learn/parse.py`: a state-machine parser that splits a response into
# `reply` and `notes` given `<agent_notes>` tags. Test it on hand-written edge
# cases (missing notes, unclosed tag, tag mentioned in prose) *before* any
# model output touches it. This file is reused unchanged in module 8.

import re
import pathlib
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import (
    CORRECT, INCORRECT, PARTIAL, Score, Target, accuracy, exact, includes, match,
    mean, model_graded_qa, pattern, scorer, stderr
)
from inspect_ai.solver import TaskState, generate


@scorer
def strict():
    async def score(state: TaskState, target: Target) -> TaskState:
        got = state.output.completion.strip()
        if got == target.text:
            value = CORRECT
            return Score(value)
        else:
            value = INCORRECT
            answer = got
            explanation = f"expected exactly {target.text!r}"
            return Score(value, answer, explanation)
    return score