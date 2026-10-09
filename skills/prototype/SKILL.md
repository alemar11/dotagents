---
name: prototype
description: "Build and run isolated prototypes, spikes, or proofs of concept to test UI, interaction, logic, or state behavior. Use when a runnable experiment is requested, in the project's stack or as a standalone example; not for production implementation or read-only comparisons."
---

# Prototype

Build the smallest experiment that can resolve the user's question. Choose the
language, runtime, and execution surface from the project and the behavior being
tested. A native app question does not imply an HTML demo.

## Frame the experiment

Reuse the question, scope, constraints, and accepted decisions already in the
conversation. On a bare `$prototype` invocation, infer the experiment from that
context and inspect the relevant project. If no concrete question is apparent,
ask what decision the experiment should settle; do not build a generic sample.

Identify the observable result that would support or reject the idea before
building. Inspect the relevant source, project instructions, dependencies, and
run configuration. Ask only when a material choice cannot be inferred, such as
which interaction or platform the user wants to compare.

A request to build a prototype authorizes the local experiment and its isolated
workspace. Automatic selection does not turn discussion or read-only planning
into permission to write. A read-only caller may recommend an experiment and
return its question and scope; building begins only with established authority.
Prototype is optional and adds no mandatory stage to Explore, Architect, or Implement.

## Choose the execution surface

| Question | Appropriate experiment |
| --- | --- |
| Native app appearance, interaction, or navigation | Use the app's actual UI framework, such as SwiftUI, UIKit, React Native, or Android UI, and exercise it on an appropriate simulator, emulator, or device. |
| Web UI or browser behavior | Use the existing web stack and inspect the rendered experiment in a browser. |
| Logic, algorithms, or state transitions | Use a small executable or harness in the project's language, with visible inputs, transitions, and results. |
| Platform-independent idea with no project integration needed | Use a standalone artifact, including interactive HTML when it is sufficient to answer the question. |

Match fidelity to the decision. Use real navigation, keyboard, lifecycle, or
platform behavior when it is what the experiment tests. A mocked transition or
browser approximation cannot establish that native behavior works. Compare
distinct alternatives only when a comparison is needed, using the same scenario
for each; do not manufacture a fixed number of variants.

## Isolate the work

Use a unique temporary directory for a self-contained example. For an experiment
that needs an app's components, assets, dependencies, or build configuration,
use an isolated worktree of that project. Respect an explicitly supplied scratch
workspace and the existing worktree manager when one owns the checkout.

Verify the source repository and base revision. If relevant local changes are
needed, carry only the selected changes into the isolated workspace and verify
them there; do not reset, stash, or commit the source checkout to obtain a clean
base. A non-Git project can use a scoped disposable copy. If isolation cannot
preserve the required inputs, report the limitation before changing shared files.

Keep experimental entry points visibly named as prototypes and follow the
project's layout. Reuse its toolchain and dependency versions; avoid introducing
a second framework merely to make a demo easier. Temporary storage describes
the artifact's location, not permission to delete it after reporting success.

## Build and exercise

Implement only enough behavior and presentation to answer the question. Reuse
real components where their behavior matters, with fixture data or controlled
adapters for unrelated services. Keep state in memory by default. Experiments
about persistence use isolated local storage or an authorized disposable
environment, never an existing user store merely because the app can reach it.
External writes and production actions require their own authorization.

Expose the relevant state and make the scenario easy to repeat or reset. Do not
create reusable architecture, a broad test suite, or production polish for the
experiment. Add a focused check when it is the cheapest reliable way to prove
the disputed behavior; retain any required build or execution checks.

Build and run with the appropriate project commands. For UI questions, exercise
the actual rendered interaction on the selected platform; compilation, static
screenshots, and a preview that omits the disputed behavior are insufficient.
For logic questions, run the relevant cases and inspect their outputs. Record
the environment and observations that support the conclusion, distinguishing
simulated dependencies from behavior actually exercised.

If the required SDK, runtime, device, credentials, or interaction capability is
unavailable, report exactly which proof is missing. Do not silently substitute
a different platform or claim a runnable artifact was verified without running
it. Deliver any useful artifact with its unverified parts clearly identified.

## Handoff and lifetime

Return the question, result, supporting observations, and remaining uncertainty.
Include the artifact or worktree location and exact launch instructions, with
any fixtures or limitations needed to interpret it. Distinguish an observed
technical result from a design preference that still needs the user's reaction.
Stop when the experiment answers the question or the missing proof is clear.

Leave the artifact available for inspection; temporary paths may be cleaned by
the operating system, so disclose that lifetime. Report any preview left running
and how to stop it. Stop obsolete processes started for the experiment without
interrupting unrelated work. Remove artifacts or worktrees only when cleanup is
requested and their contents have been reconciled.

The result is evidence for the next decision. Do not automatically promote it
into production, commit, push, open issues or PRs, or persist project decisions.
Carry out separately authorized follow-up through the workflow that owns it,
preserving the experiment until its evidence is no longer needed.
