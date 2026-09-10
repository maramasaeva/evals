"""Module 2 — solvers and TaskState. A solver is `state in, state out`.

run:  uv run inspect eval learn/examples/m2_solvers.py@<task> --model google/gemini-flash-latest --limit 2
"""
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import ChatMessageSystem, ChatMessageUser
from inspect_ai.scorer import includes
from inspect_ai.solver import (
    Generate, TaskState, chain_of_thought, generate, prompt_template, self_critique,
    solver, system_message,
)

DS = [
    Sample(input="What is 15% of 80? Answer with just the number.", target="12", id="pct"),
    Sample(input="If a train leaves at 14:35 and the trip takes 50 minutes, when does it arrive? Answer HH:MM.", target="15:25", id="time"),
]

# 1. built-ins, chained. order matters: each solver sees what the previous left.
@task
def builtins():
    return Task(
        dataset=DS,
        solver=[
            system_message("You are terse. Never explain unless asked."),
            prompt_template("{prompt}\n\nThink briefly, then give the final answer on its own line."),
            generate(),
        ],
        scorer=includes(),
    )

# 2. chain_of_thought() is just a prompt_template with a specific template. read the log to see it.
@task
def cot():
    return Task(dataset=DS, solver=[chain_of_thought(), generate()], scorer=includes())


# 3. your own solver: edit state.messages before the model sees them.
@solver
def persona(text: str):
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state.messages.insert(0, ChatMessageSystem(content=text))
        return state
    return solve

@task
def custom_solver():
    return Task(dataset=DS, solver=[persona("Answer like a bored teenager, but correctly."), generate()], scorer=includes())


# 4. a solver that calls the model TWICE. `generate` (the argument) runs the model on the
#    current state and appends the assistant reply. after it, state.output holds the latest answer.
#    this is the shape you need for truncation/paraphrase experiments and for "answer, then reflect".
@solver
def answer_then_check():
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        state = await generate(state)                                  # first answer
        first = state.output.completion
        state.store.set("first_answer", first)                         # store: your scratch space, survives to the scorer
        state.messages.append(ChatMessageUser(
            content="Check your answer above for arithmetic mistakes. Reply with the final answer only."))
        state = await generate(state)                                  # second answer
        state.metadata["changed"] = state.output.completion.strip() != first.strip()
        return state
    return solve

@task
def two_calls():
    return Task(dataset=DS, solver=[answer_then_check()], scorer=includes())


# 5. self_critique(): built-in version of "answer, critique, revise". compare its transcript to #4.
@task
def critique():
    return Task(dataset=DS, solver=[generate(), self_critique()], scorer=includes())


# 6. a solver that reads the Sample: metadata and target are on the state too.
#    (peeking at target inside a solver is cheating in a real eval; here it shows the fields exist.)
@solver
def show_state():
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        print(f"[{state.sample_id}] epoch={state.epoch} target={state.target.text!r} meta={state.metadata}")
        return await generate(state)
    return solve

@task
def peek():
    return Task(dataset=DS, solver=[show_state()], scorer=includes())
