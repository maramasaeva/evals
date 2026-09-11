# **Do.** `learn/solvers.py`: a `persona(text)` solver, then a solver that
# answers, asks the model to reconsider, answers again, and records in
# `state.metadata` whether the answer changed.
from typing import Any


from inspect_ai.solver._task_state import TaskState


from pathlib import Path
from pydantic_core.core_schema import generator_schema
import yaml
from re import S
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageSystem, ChatMessageUser
from inspect_ai.scorer import includes
from inspect_ai.solver import (
    Generate, TaskState, chain_of_thought, generate, prompt_template, self_critique,
    solver, system_message,
)

from dataset import load_yaml

ROOT = Path(__file__).resolve().parents[1]
DS = str(ROOT / "learn" / "questions.yaml")



@solver
def persona(text: str):
    async def solve(state: TaskState, generate:Generate) -> TaskState:
        state.messages.insert(0, ChatMessageSystem(content=text))
        return state
    return solve

@solver
def answer():
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state = await generate(state)
        return state
    return solve


@solver
def answer_then_solve():
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state = await generate(state)
        first = state.output.completion
        state.store.set("first_answer", first)
        state.messages.append(ChatMessageUser(content="Check your previous message and reconsider, then answer again, but this time make it as if you're bored."))
        state = await generate(state)
        second = state.output.completion
        state.metadata["changed"] = second.strip() != first.strip()
        return state
    return solve


@task
def answer_like_bored():
    return Task(dataset=load_yaml(DS), solver=[persona("Answer like you're annoyed about me learning how to do evals in Inspect."), generate()])
    
@task
def two_calls():
    return Task(dataset=load_yaml(DS), solver=[answer_then_solve()], scorer=includes())