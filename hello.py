from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.solver import generate


@task
def hello():
    return Task(
        dataset=[Sample(input="Reply with exactly the word: Hello", target="Hello")],
        solver=[generate()],
        scorer=includes(),
    )
