# Gate Event Contract

Load only when the controller applies current validation, scope, or gate
evidence. `ledger-cache` owns the generic envelope, common bindings, CAS, and
typed template. This file owns the gate event families.

| event | phase-specific inputs and evidence |
| --- | --- |
| `validation-nonregression-observed` | Task/delivery/validation and revision identities, adapter/policy, argv/tool fingerprints, complete diagnostics/set fingerprint, and evidence. |
| `delivery-scope-observed` | Task/delivery/revision identities, canonical changed paths, untracked paths, and evidence. |
| `gate-observed` | Task, nullable delivery, gate, passed/failed state, canonical scope binding, current task observation, and evidence. |

Gate scopes are closed:

| scope | gates | identity |
| --- | --- | --- |
| task static | `dependency-integration` | no delivery or revision binding |
| delivery revision | `focused-validation`, `full-validation`, `autoreview`, `publication`, `codex-review`, conditional `ci`, `pr-ready`, `tracker-closeout`, `mergeability` | delivery plus current delivery-evidence key |
| task revision set | `scope-acceptance`, `integration-validation`, optional `domain-closeout` | complete current delivery revision set |

Gate state is only `passed|failed`. CI evidence is illegal for
`not-configured`. Changed revision, preflight, CI availability, PR identity,
diff, rules, tracker delivery, evidence target, or relevant documentation
invalidates the corresponding delivery and task-set proof.

The exact warning-backed `timeout-accepted` GitStack outcome may pass only the
Codex-review gate. It remains a warning and never becomes a clean verdict or
overrides any other gate.
