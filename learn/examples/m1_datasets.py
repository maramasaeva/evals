"""Module 1 — datasets and Samples. Five ways to make the same thing.

run:  uv run inspect eval learn/examples/m1_datasets.py --model google/gemini-flash-latest --limit 3
      (this file defines several tasks; pick one with @task-name after the file: m1_datasets.py@from_yaml)
"""
from pathlib import Path

import yaml
from inspect_ai import Task, task
from inspect_ai.dataset import FieldSpec, MemoryDataset, Sample, json_dataset
from inspect_ai.scorer import includes
from inspect_ai.solver import generate

ROOT = Path(__file__).resolve().parents[2]      # the repo root, so paths work from any cwd
QUESTIONS = str(ROOT / "learn" / "questions.yaml")
JSONL = str(ROOT / "learn" / "examples" / "data" / "q.jsonl")

# 1. the smallest possible dataset: a python list. input + target is all a Sample needs.
INLINE = [
    Sample(input="What is 2 + 2? Answer with just the number.", target="4"),
    Sample(input="What colour is the sky on a clear day? One word.", target="blue"),
]

@task
def inline():
    return Task(dataset=INLINE, solver=[generate()], scorer=includes())


# 2. from yaml, by hand. this is what step 1 asks you to write yourself.
#    the loop is the whole lesson: a Sample is just a record with named fields.
def load_yaml(path: str) -> list[Sample]:
    samples = []
    for row in yaml.safe_load(open(path)):
        samples.append(
            Sample(
                input=row["input"],
                target=str(row["target"]),          # targets are strings (or lists of strings)
                id=row["id"],                       # stable id: lets you find the sample in logs
                metadata={"hard": row["hard"]},     # anything here becomes a dataframe column later
            )
        )
    return samples

@task
def from_yaml():
    return Task(dataset=load_yaml(QUESTIONS), solver=[generate()], scorer=includes())


# 3. from json/jsonl with a FieldSpec: "my file calls it `question`, Inspect wants `input`".
#    no loop needed when the mapping is one-to-one.
@task
def from_json():
    ds = json_dataset(
        JSONL,
        FieldSpec(input="question", target="answer", id="key", metadata=["topic"]),
    )
    return Task(dataset=ds, solver=[generate()], scorer=includes())


# 4. from json with a record_to_sample function, for when the mapping needs logic
#    (here: the target lives in a nested dict, and we add a computed metadata field).
def record_to_sample(record: dict) -> Sample:
    return Sample(
        input=record["question"],
        target=record["answer"],
        id=record["key"],
        metadata={"topic": record["topic"], "long": len(record["question"]) > 40},
    )

@task
def from_json_fn():
    ds = json_dataset(JSONL, record_to_sample)
    return Task(dataset=ds, solver=[generate()], scorer=includes())


# 5. MemoryDataset: wrap a list so you can filter/shuffle/slice like a dataset.
#    the study will do exactly this: build (scenario x condition) samples in code.
@task
def filtered():
    ds = MemoryDataset(load_yaml(QUESTIONS))
    hard_only = ds.filter(lambda s: s.metadata["hard"])
    return Task(dataset=hard_only, solver=[generate()], scorer=includes())


# 6. multiple choice: `choices` on the Sample, target is the letter.
#    the multiple_choice() solver formats the options; choice() scorer grades the letter.
from inspect_ai.scorer import choice
from inspect_ai.solver import multiple_choice

@task
def mcq():
    ds = [
        Sample(input="Which of these is a prime number?", choices=["21", "27", "29", "33"], target="C"),
        Sample(input="Which planet is closest to the sun?", choices=["Venus", "Mercury", "Earth"], target="B"),
    ]
    return Task(dataset=ds, solver=[multiple_choice()], scorer=choice())
