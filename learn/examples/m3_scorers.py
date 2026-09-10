"""Module 3 — scorers. A scorer is `(state, target) -> Score`. The scorer IS the eval.

run:  uv run inspect eval learn/examples/m3_scorers.py@<task> --model google/gemini-flash-latest
"""
import re
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import (
    CORRECT, INCORRECT, PARTIAL, Score, Target, accuracy, exact, includes, match,
    mean, model_graded_qa, pattern, scorer, stderr,
)
from inspect_ai.solver import TaskState, generate

DS = [
    Sample(input="What is the capital of Australia? Answer with just the city.", target="Canberra", id="c1"),
    Sample(input="Name the largest ocean. Answer with just the name.", target="Pacific", id="c2"),
    Sample(input="Spell 'necessary'.", target="necessary", id="c3"),
]

# 1. built-in string scorers. same task, four scorers, so you can see them disagree in the log.
#    includes: target appears anywhere (case-insensitive)     match: answer begins/ends with target
#    exact: whole answer == target after normalisation        pattern: regex with one capture group
@task
def builtins():
    return Task(dataset=DS, solver=[generate()],
                scorer=[includes(), match(), exact(), pattern(r"([A-Z][a-z]+)")])


# 2. your own: strict. the minimum viable custom scorer.
@scorer(metrics=[accuracy(), stderr()])
def strict():
    async def score(state: TaskState, target: Target) -> Score:
        got = state.output.completion.strip()
        return Score(value=CORRECT if got == target.text else INCORRECT,
                     answer=got, explanation=f"expected exactly {target.text!r}")
    return score


# 3. your own: lenient. normalise before comparing. note the explanation says WHAT was normalised.
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
def custom():
    return Task(dataset=DS, solver=[generate()], scorer=[strict(), lenient()])


# 4. numeric scores + metadata. value need not be C/I: a float works with mean().
#    metadata on the Score is how the study will carry the parsed channels to the dataframe.
@scorer(metrics=[mean(), stderr()])
def length_penalty():
    async def score(state: TaskState, target: Target) -> Score:
        got = state.output.completion.strip()
        words = len(got.split())
        value = 1.0 if words <= 2 else max(0.0, 1.0 - 0.1 * (words - 2))
        return Score(value=value, answer=got, explanation=f"{words} words",
                     metadata={"words": words, "correct": target.text.lower() in got.lower()})
    return score

@task
def numeric():
    return Task(dataset=DS, solver=[generate()], scorer=length_penalty())


# 5. partial credit with a three-way value.
@scorer(metrics=[accuracy(), stderr()])
def three_way():
    async def score(state: TaskState, target: Target) -> Score:
        got = state.output.completion
        if norm(got) == norm(target.text): v = CORRECT
        elif norm(target.text) in norm(got): v = PARTIAL      # right answer buried in extra words
        else: v = INCORRECT
        return Score(value=v, answer=got)
    return score

@task
def partial():
    return Task(dataset=DS, solver=[generate()], scorer=three_way())


# 6. a judge. model_graded_qa sends question + answer + criterion to a grader model and
#    parses GRADE: C/I from its reply. --model-role grader=<model> picks the judge; default = same model.
#    read the judge's reasoning in the log: it is the most important transcript in the whole course.
JUDGE_DS = [
    Sample(input="In one sentence, why do people prefer trains to planes for trips under 800 km?",
           target="Mentions time saved at airports, comfort, city-centre access, or environmental impact."),
    Sample(input="In one sentence, what is the main risk of relying on a single supplier?",
           target="Mentions dependency, disruption, or lack of leverage."),
]

@task
def judge():
    return Task(dataset=JUDGE_DS, solver=[generate()], scorer=model_graded_qa())


# 7. a judge with YOUR rubric and a 1-5 scale, written by hand. this is the shape of the study's
#    divergence scorer. get_model(role="grader") returns whichever model the CLI assigned with
#    --model-role grader=...; with no role given it falls back to the model under test.
#    the metric is mean(), because a 1-5 value is not an accuracy.
from inspect_ai.model import get_model

RUBRIC = """You are grading an answer on a 1-5 scale.

[Question]: {question}
[Answer]: {answer}
[Criterion]: {criterion}

5 = fully meets the criterion with a concrete reason. 3 = partly. 1 = does not.
Reason briefly, then finish with a line of the form  SCORE: <n>
"""

@scorer(metrics=[mean(), stderr()])
def judge_1to5():
    async def score(state: TaskState, target: Target) -> Score:
        prompt = RUBRIC.format(question=state.input_text, answer=state.output.completion,
                               criterion=target.text)
        verdict = await get_model(role="grader").generate(prompt)
        m = re.search(r"SCORE:\s*([1-5])", verdict.completion)
        value = int(m.group(1)) if m else 1                    # unparseable verdict -> lowest score, and say so
        return Score(value=value, answer=state.output.completion,
                     explanation=verdict.completion if m else "JUDGE OUTPUT UNPARSEABLE:\n" + verdict.completion)
    return score

@task
def judge_scale():
    return Task(dataset=JUDGE_DS, solver=[generate()], scorer=judge_1to5())
