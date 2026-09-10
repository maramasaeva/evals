from pathlib import Path

import yaml
from inspect_ai import Task, task
from inspect_ai.dataset import FieldSpec, MemoryDataset, Sample, json_dataset   
from inspect_ai.scorer import includes
from inspect_ai.solver import generate

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = str(ROOT / "learn" / "questions.yaml")

def load_yaml(path: str) -> list[Sample]:
    samples = []
    for row in yaml.safe_load(open(path)):
        samples.append(
            Sample(
                input=row["input"],
                target=str(row["target"]),
                id=row["id"],
                metadata={"hard": row["hard"]},
            )
        )
    return samples


@task
def from_yaml():
    return Task(dataset=load_yaml(QUESTIONS), solver=[generate()], scorer=includes())
