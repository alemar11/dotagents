# Maintenance Router

Use only under the explicit invocation boundary in `SKILL.md`. Select the route
from the request; a package name narrows scope but never turns a review into an
edit. Route identifiers and result values are owned by [states.md](states.md).

## Routes

| Mode | Request | Read |
| --- | --- | --- |
| `maintain` | Bare invocation, run, or maintenance of named packages | [run-maintenance.md](run-maintenance.md), restricted to named packages when supplied |
| `maintain` | Improve, rename, move, merge, replace, or remove named existing packages as requested | [skill-upgrade.md](skill-upgrade.md) |
| `maintain` / `description-review` | Metadata alignment or description review | [metadata-sync.md](metadata-sync.md) |
| `audit` | Audit or dry-run of routine maintenance | [run-maintenance.md](run-maintenance.md), read-only |
| `audit` | Specifically requested health, structure, policy, or pre-release review | [skill-health.md](skill-health.md) |
| `instruction-density` | Review or refactor instruction density | [instruction-density-review.md](instruction-density-review.md) |
| `workflow-hardening` | Explicit request or connected defect found during routine maintenance | [workflow-family-hardening.md](workflow-family-hardening.md) |
| `refresh` | Swift-DocC refresh/freshness request or routine maintenance | [swift-docc-refresh.md](swift-docc-refresh.md), [swift-docc-runbook.md](swift-docc-runbook.md) |
| `refresh` | Swift API Design refresh/freshness request or routine maintenance | [swift-api-design-refresh.md](swift-api-design-refresh.md), [swift-api-design-runbook.md](swift-api-design-runbook.md) |
| `okf-spec` | OKF spec comparison/refresh request or routine maintenance | [okf-spec-refresh.md](okf-spec-refresh.md), [okf-spec-runbook.md](okf-spec-runbook.md) |

For capability questions, read [task-menu.md](task-menu.md) without starting a
maintenance run. Brand-new skills or plugins start with their creator workflow;
substantial reshapes do too, followed by targeted maintenance here.

An audit-and-fix request gathers evidence through its review playbook, then
applies authorized findings through targeted maintenance. Routine maintenance
includes all applicable source refresh routes; a named package limits them to
that package. A named operation limits work to that operation. Preserve any
read-only constraint across every branch. For TanStack, maintain the
`project-tools` reference against official Intent consumer guidance, not a
local API skill catalog; this does not invoke its installation workflow.

## Mixed work and delegation

Select only necessary routes. Establish behavior and ownership before
restructuring, resolve package changes before metadata alignment, and validate
the resulting artifact. For behavior-sensitive description changes, use the
instruction-density criteria first. Reuse evidence across routes.

When runtime policy permits and delegation helps, delegate independent read-only
slices or disjoint edits. Keep routing, integration, finding severity, and final
Git verification in the main agent. Visible user-owned Codex App tasks still
require applicable explicit permission.

## Shared completion

Branch playbooks return their evidence to one
[release-checklist.md](release-checklist.md) pass. Nested playbooks do not repeat
metadata alignment, health checks, validation, or closeout already owned by the
caller. Repeat a check only after relevant changes or new evidence invalidate it.
