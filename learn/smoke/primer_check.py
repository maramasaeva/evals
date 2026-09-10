from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageSystem
from inspect_ai.scorer import Score, Target, scorer, accuracy, stderr, CORRECT, INCORRECT
from inspect_ai.solver import Generate, TaskState, generate, solver

@solver
def persona(text: str):
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state.messages.insert(0, ChatMessageSystem(content=text))
        return state
    return solve

@scorer(metrics=[accuracy(), stderr()])
def strict():
    async def score(state: TaskState, target: Target) -> Score:
        got = state.output.completion.strip()
        return Score(value=CORRECT if got == target.text else INCORRECT,
                     answer=got, explanation=f"expected {target.text!r}")
    return score

@task
def primer_check():
    return Task(dataset=[Sample(input="Capital of Belgium? One word.", target="Brussels")],
                solver=[persona("You answer with a single word, no punctuation."), generate()],
                scorer=strict())
