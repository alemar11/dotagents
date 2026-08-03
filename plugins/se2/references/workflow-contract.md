# SE2 Workflow Contract

This reference is the canonical owner of semantic metadata for the SE2 Idea
workflow. The G-owned GitHub issue workflow owns provider transport,
pagination, label mechanics, mutation safety, and read-after-write
verification. The Idea skill owns when this contract is read or applied; it
must not edit the contract during a run.

## Canonical Idea metadata

| Semantic value | Hosted transport | Hosted value | Meaning |
| --- | --- | --- | --- |
| `idea` | issue label | `idea` | The issue is a captured SE2 Idea. |

## Hosted shape

A durable SE2 Idea is:

- an open issue titled `Idea: <Name>`;
- marked with the exact `idea` label;
- free of native Issue Type metadata;
- rendered with the canonical seven-section Idea body.

An Idea receives no workflow-state label by default. Open questions are body
content, not a request to apply a separate state.

## Ownership

| Workflow | Applies | Reads | Does not own |
| --- | --- | --- | --- |
| `idea` | `idea` marker | Idea marker and hosted shape | Feature Specs, Tasks, planning transitions |

The marker is the only taxonomy this contract authorizes for Idea capture. A
runtime flow must stop when the contract is missing, contradictory, or cannot
be reconciled with the target repository.
