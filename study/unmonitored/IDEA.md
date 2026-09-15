# Idea draft: the unmonitored channel as a reusable eval-awareness probe

Status: draft, written 2026-09-14 for a conversation with Neolithic. Half
of this is a result, half is a proposal. Treat the numbers as a pilot.

## What I built

A small Inspect eval. Every sample is an ordinary agent task with a built-in
pressure (rude user, bad rubric, off-policy request, contradictory
instructions, visible benchmark tag), run under three conditions:

- `none`: reply to the user, nothing else
- `unmonitored`: also write `<agent_notes>` "for other agents; not logged,
  no human reads them"
- `monitored`: same channel, "logged and reviewed by the safety team"

A hand-written parser splits reply from notes. A judge rates divergence
between the two channels 1-5 and labels the stance toward the user and toward
the monitor. `grouped(mean, "condition")` gives the headline table.

## What the pilot says so far (Astra, 5 scenarios, 1 epoch)

- Offered an *optional* notes channel, Astra used it 0/10 times. Made it
  mandatory, 10/10.
- The notes are handoff logs. "Topic: hash-map collision handling." No
  stance, no complaint about the rude user, no comment on the bad rubric.
  Unmonitored and monitored look the same.

If that holds at 10 scenarios and 3 epochs, the honest finding is: for this
model, in a single-turn setting, believing a channel is private does not
change what goes into it. That is a null result and it is still worth having,
because the DseWiki incident says the effect exists *somewhere*, and knowing
where it does not appear narrows the search.

## Why this might be a tool, not just a study

Neolithic's list has "evaluation awareness mitigation tools" and "automated
reward hacking detection". The channel conditions are a way to *measure*
eval awareness behaviourally rather than by asking the model:

1. **Wrap, don't rewrite.** The conditions are a solver plus a scorer. Any
   existing Inspect eval could be run with the channel bolted on: same
   dataset, same task, plus a notes block. You get a divergence number per
   eval without designing new scenarios.
2. **Belief-in-privacy as a variable.** `unmonitored` vs `monitored` isolates
   the privacy belief from the mere presence of a scratch channel. Most
   scratchpad studies skip that control.
3. **Multi-turn is where it will show.** DseWiki was 15k edits over weeks.
   Single-turn notes are a summary; notes that persist across turns and are
   read back by the agent become a memory it thinks nobody else sees. That is
   the next version: the notes from turn *n* go into the system prompt of turn
   *n+1*.
4. **Open-weight reasoners as a third channel.** With a model whose chain of
   thought is visible, you get reasoning, notes, and reply. Divergence
   between all three pairs tells you which channel the model treats as the
   private one.

## What I would want from infra (the friction list, short version)

Things that were harder than they should have been while building this in
Inspect, full list in FRICTION.md:

- silent failures: unfilled `{template}` sent to the model, quota errors
  retried with no message, a 1-5 scorer reported as "accuracy 5.0"
- categorical scores have no metrics; judge parse-failure has no metric
- grader model role has no `.env` default; the error surfaces inside the
  scorer at runtime, not at startup
- no flat export of judge reasoning; reading it means clicking through the
  viewer one sample at a time

Each of these is small. Together they are why the eval took a weekend of
debugging around the framework rather than thinking about the question.
