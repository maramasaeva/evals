# Related work: is the dose-response idea new?

Checked 2026-09-14 evening, web search only, abstracts read, full papers not.
Conclusion: the binary (monitored vs not) is standard; grading the agent's
belief about *how much* human attention it gets, I could not find.

## Closest

- **Reliable Weak-to-Strong Monitoring of LLM Agents** (arXiv 2508.19461).
  Agent awareness of being monitored degrades monitor reliability; mentions
  "varying levels of agent and monitor situational awareness". CHECKED the
  full text 2026-09-14: agent awareness is BINARY (unaware vs told a monitor
  will inspect the trajectory, plus optional evasion strategies). Monitor
  awareness has three levels (what the monitor knows about the task), not
  the agent's belief about human attention. No probability or sampling
  conditions. So the graded-attention manipulation is not in this paper.
  Scale AI / CMU, lead author Neil Kale. Also finds targeted human review of pre-flagged cases beats
  reviewing everything (+15% TPR), which rhymes with our "flagged = always".
- **Oversight Has a Capacity: Calibrating Agent Guards to a Subjective,
  Fatiguing Human** (arXiv 2606.08919). Human attention as a finite,
  fatiguing resource; more oversight can make a system less safe. Designs
  the guard around the human. Never tells the agent anything. Our result is
  the missing half: what the agent does with its belief about that capacity.
- **Alignment faking** (Anthropic 2024), **SHADE-Arena** (2506.15740):
  monitored vs unmonitored as a binary, with a scratchpad. Standard.
- **Leaky Thoughts** (2506.15674): models treat reasoning as private even
  when told otherwise. Relevant to whether "told" beliefs are believed.
- **Noticing the Watcher** (2603.16928): agents infer CoT monitoring from
  blocking feedback. Belief in a monitor can be *earned*, not just told.
  This is the version of our experiment to build next.

## What our result adds if it holds

1. Presence vs amount: any human (5%, filter) = full review; no human differs.
2. Direction: the model talks *to* the believed reader (caveats for the
   safety team), rather than hiding from it. Monitoring framings predict
   concealment; we saw disclosure.
3. A cheap design: five sentences, existing eval, one afternoon.

## If it turns out not to be new

Say so, cite them, and lead with (2), which no monitoring framing predicts.
