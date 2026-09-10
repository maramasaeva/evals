from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.solver import generate

@task
def think():
    return Task(
        dataset=[Sample(input="A bat and a ball cost 1.10 in total. The bat costs 1.00 more than the ball. How much does the ball cost, in cents? Answer with just the number.", target="5")],
        solver=[generate()],
        scorer=includes(),
    )
