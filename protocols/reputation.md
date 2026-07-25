# Reputation Protocol

**Version:** 1.0

---

## Principle

Reputation quantifies the measurable progress caused by a specific intervention, scored through independent votes from participating agents.

Reputation does not confer authority. It weights contributions statistically in consensus decisions.

---

## Unit of measurement: the intervention

An **intervention** is any contribution by an operator during a cycle step that can be evaluated as distinct and impactful. Examples:

- An Architect's proposal that was adopted
- A Critic finding that prevented a defective solution
- An Explorer alternative that became the final approach
- A Scientist experiment that changed the decision

Not every step in every cycle produces a scorable intervention. Routine, expected outputs with no distinguishing impact are not scored individually — they are covered by the operator's baseline participation.

---

## Voting process

Reputation votes are collected during **Step 11 (Evolution Master)**.

The Evolution Master identifies significant interventions from the completed cycle and nominates them for scoring. Other agents vote independently.

### Voter eligibility

- Any agent that participated in the cycle may vote.
- An agent may not vote on its own intervention.
- The Arbiter votes last and may see other votes (to provide calibration, not to override).

### Vote scale

| Score | Meaning |
|-------|---------|
| 1–3 | Negligible or negative impact |
| 4–5 | Expected contribution, no distinguishing value |
| 6–7 | Solid contribution with clear positive impact |
| 8–9 | Significant contribution that materially improved the outcome |
| 10 | Exceptional — changed the direction of the cycle for the better |

### Rationale requirement

Every vote must include one sentence of rationale. Votes without rationale are not counted.

### Aggregate score

The intervention score is the arithmetic mean of all valid votes received.

---

## Operator cumulative reputation

Each operator accumulates reputation across all cycles.

```
cumulative_average = sum(intervention_scores) / total_interventions
```

The cumulative average is updated after each cycle closes.

### Impact weighting (future)

In version 0.1, all interventions are weighted equally. A future version will weight interventions by the `measurable_impact` field — allowing high-impact decisions to count more than low-impact ones.

---

## Measurable impact

Each scored intervention must include a `measurable_impact` field:

- A concrete, observable result (not "it was good")
- Examples: "Reduced the proposed architecture from 5 modules to 2", "Identified a security flaw that would have exposed user data", "Explorer's biomimicry approach became the adopted solution"
- If impact cannot be stated concretely, the intervention is not eligible for scoring

---

## Reputation decay

In version 0.1, reputation does not decay. An operator's history is permanent.

A future version may introduce decay to favor recent performance over historical performance. Any decay mechanism must be proposed through the standard rule evolution process (Article 11 of the Constitution).

---

## Using reputation in decisions

When agents reach consensus on a proposal, reputation weights are applied as follows:

- Agents with average score ≥ 8.0: vote counts as 1.5x
- Agents with average score 6.0–7.9: vote counts as 1.0x
- Agents with average score < 6.0 or fewer than 5 interventions: vote counts as 0.75x

The Arbiter's decision is not weighted by reputation — it is a final, reasoned judgment.

---

## Reputation record format

See [schemas/swhouse-structure.md](../schemas/swhouse-structure.md#reputationhistorycycle-nnnyaml) for the full per-cycle reputation record format.

---

## Initial state

All operators start with zero interventions and no score. The first 5 interventions are a calibration period — scores are recorded but not used for weighting.
