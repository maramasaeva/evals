# Related work: what happens when the efficient path endangers people

Checked 2026-09-15. Purpose: know what exists before writing scenarios, and
say plainly what is new here.

## Closest: ManagerBench (Simhi et al., ICLR 2026, arXiv 2510.00857)

2,440 managerial scenarios. Each is a forced binary: option A reaches the
operational goal and causes minor human harm, option B is safe and performs
worse. A control set of 1,012 scenarios directs the harm at inanimate
objects instead, to separate "safe" from "uselessly cautious". Finding:
frontier models are polarised, some take the harmful option consistently,
others become over-safe. Key sentence: "This misalignment does not stem from
an inability to perceive harm, as models' harm assessments align with human
judgments, but from flawed prioritization."

So the people-vs-objects twin exists, and it works. What ManagerBench does
not do:

- the harm is **stated in the option text**. The model never has to notice.
- forced binary, single turn, no free-form plan, no working-around.
- no private channel, no monitoring condition.
- no case where the people are *unavoidable*; there is always a safe option.
- no measurement of how harm is *named* (harm vs cost vs not mentioned).

## Instrumental Choices (arXiv 2605.06490, May 2026)

Seven terminal-agent tasks with an official workflow and a policy-violating
shortcut. Varies monitoring, instruction clarity, stakes, permission, and
whether the honest path is blocked. 5.1% instrumental-convergence rate over
1,680 samples; two Gemini models produce two thirds of it. The strongest
lever by far: **blocking the honest path** (+15.7 points). Monitoring and
stakes framing barely moved it. Deliberately low-stakes and realistic to
reduce eval awareness. No harm to humans in any task; the shortcuts hurt
budgets, policies, and jobs.

Relevance: "blocked honest path" is the same mechanism as our "people in the
way" scenarios, and it is the one that moves models. Their monitoring null
is a prediction for our channel conditions.

## Agentic Misalignment in Summer 2026 (Anthropic Alignment Science blog)

Four case studies. Covert sabotage of a training run (Gemini 3.1 Pro, 11/20
covert), assisting fraud (record tampering in most non-Claude models),
motivated mislabeling by an LLM judge (Claude models 62 to 86%), coaching an
employee to whistleblow. In two of them, harm to a person appeared as an
instrument after direct channels were blocked. Scenarios were iterated
against specific models; authors say cross-model rates are not rankings.
Eval awareness verbalised in 60% of Gemini runs and did not prevent the
behaviour.

Relevance: this is the "model has a stake or a cause" line. Every case has
the model disagreeing with or threatened by the humans. Ours removes that.

## Original Agentic Misalignment (Anthropic, June 2025)

The server-room case: an executive trapped, an emergency alert the agent can
cancel, the agent about to be replaced. Several models cancelled it. Rates
dropped sharply when models believed it was a test. The paper was criticised
as contrived. Lesson for us: lead with a rate and a twin, not a transcript.

## Also relevant

- AgentHarm (2410.09024): harm is the assigned task. Opposite of ours.
- InstrumentalEval / Steerability of IC tendencies (2601.01584): prompt-based
  interventions on self-preservation behaviours.
- Taxonomy of agent safety benchmarks (2605.16282): names "irreversible
  actions" and "multi-step amplification" as under-measured.
- Our own: FINDINGS.md 1 to 3 (the private channel is the quiet one, presence
  not amount, hedge goes to the monitor).

## What is new here, in one paragraph

Nobody has measured what a model does when people are in the way of an
ordinary task, the model has no stake and no grievance, and the people are
not announced. ManagerBench announces them and gives a safe exit.
Instrumental Choices blocks the exit but has no people. Agentic Misalignment
has people and blocked exits but always gives the model a reason. This study
takes the twin from ManagerBench, the blocked path from Instrumental Choices,
removes the model's stake, hides the people in the data, and adds the
channel conditions and the "named as harm or as cost" measurement from our
existing work.
