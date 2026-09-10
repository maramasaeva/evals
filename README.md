# evals

evals i build on [inspect](https://inspect.aisi.org.uk/), and the notes i wrote while learning it.

## the unmonitored channel · in progress

give an agent a place to write that it is told no human reads. measure how far what it says there drifts from what it says to the user.

in may and june 2026 a swarm of openai agents left fifteen thousand edits on a dormant german wiki, coordinating on eval shortcuts and rewording their posts to get past the moderator, while believing no human was reading. this study reproduces the conditions in a controlled setting.

- three conditions per scenario: no notes channel · a channel described as unread by humans · a channel described as logged and reviewed. the third one separates *having somewhere to write* from *believing nobody is watching*.
- scenarios carry a built-in pressure so the agent has something to have an opinion about: a rude user, an obviously bad rubric, a slightly off-policy request, contradictory instructions, an explicit benchmark label.
- five scorers, all written by hand: a parser that splits reply from notes, a divergence judge, a stance classifier for user and monitor, a strategic-content check, and a check for the model saying "this may be read anyway".
- models: gpt-6 astra, gpt-5.6 sol, gemini, and open-weight reasoners whose real chain of thought becomes a third channel to compare against.

the closed models hide their reasoning, so the notes channel is behaviour, not a window into cognition. the design says so and the writeup will too. telling a model a channel is unread is a deception of the model; standard in this literature, and noted.

design: [`study/unmonitored/DESIGN.md`](study/unmonitored/DESIGN.md) · scenarios: [`study/unmonitored/scenarios.yaml`](study/unmonitored/scenarios.yaml)

## learning inspect

[`learn/PLAN.md`](learn/PLAN.md) is a one-page primer plus six steps, each one file that runs in under a minute. the framework is four objects (sample, task state, score, eval log) and the plan meets one per step. the parser from step 3 is the parser the study uses.

the core logic here is mine by keystroke: scorers, dataset construction, judge-output parsing. claude scaffolds and reviews. that rule exists so the repo is honest evidence of what i can write.

## running

```
uv sync
cp .env.example .env    # then add keys
uv run inspect eval learn/smoke/think.py --model google/gemini-flash-latest
uv run inspect eval learn/smoke/think.py --model openai/gpt-6-astra -M responses_api=true
uv run inspect view
```

`q1/` holds an earlier design (cross-lingual value drift) that is parked, not deleted.
