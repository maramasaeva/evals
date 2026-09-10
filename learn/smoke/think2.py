from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.solver import generate

@task
def think2():
    return Task(
        dataset=[Sample(input="Alice, Bob and Carol each have a different pet: a cat, a dog and a fish. Alice is allergic to fur. Bob's pet does not swim. Who has the dog? Also, briefly, how did you decide? Put the name first.", target="Bob")],
        solver=[generate()],
        scorer=includes(),
    )
