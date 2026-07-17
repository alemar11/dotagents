# Non-App Delivery Exception

Load this reference when the current user explicitly requests an implementation
stopping point outside `$implement-feature`'s fixed pull-request-ready flow, or
when a canonical durable source Feature Spec already carries exactly one
`non_app_delivery_target` and exactly one resolvable
`explicit_instruction_ref` that selected it. Do not load it for normal
App-compatible planning, and never treat either datum as mutation authority.

## Registry

| Field | Allowed values | Default |
| --- | --- | --- |
| `non_app_delivery_target` | `local-commit-created-without-pushing`, `changes-pushed-to-target-branch-without-pull-request`, `validated-draft-pull-request-published` | None; current-request selection or canonical durable-source carry-forward is required. |

## Canonical Evidence Data

`explicit_instruction_ref` is required evidence data, not an option. In the
Feature Spec's single `## Non-App Delivery` section, record exactly one line for
each datum:

```text
non_app_delivery_target: <canonical value>
explicit_instruction_ref: <portable resolvable reference>
```

The instruction ref must resolve to the exact authorized-user instruction that
selected the target for this Feature Spec scope. Accept a stable hosted URL,
tracker or document ref with enough context to retrieve the instruction, or a
runtime-provided durable task/message ref. Reject free-form quotes, vague
phrases such as "the current request", machine-local paths, missing targets,
duplicate lines, unresolved refs, or refs whose instruction selects another
target or scope. When the current request selects the exception, capture its
durable message ref before publication; withhold the artifact if the runtime
cannot provide a portable resolvable ref.

Add only `non_app_delivery_target` as a row in each generated issue's
`## Execution Contract` table. Keep `explicit_instruction_ref` once in the
owning Feature Spec so it cannot drift across issues.

## Boundary

- The presence of `non_app_delivery_target` makes the complete Feature Spec
  bundle incompatible with `$implement-feature`; state that prominently in
  the Feature Spec and issue-phase report.
- The field describes an intended observable stopping point. It does not grant
  commit, push, pull-request, tracker-mutation, or merge authority.
- The eventual non-App executor must obtain its own authorization before any
  mutation and must enforce repository policy, validation, and tracker
  lifecycle rules.
- Keep `target_branch_name`, affected repositories, allowed paths, and issue
  dependencies in the ordinary Execution Contract. Do not introduce a second
  delivery or permission tuple.
- A later request to use App orchestration requires regenerating the bundle
  without this exception; never silently drop or reinterpret the field.
