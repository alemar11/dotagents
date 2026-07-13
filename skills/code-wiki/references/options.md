# Code Wiki Option Contract

Load this reference before reporting validator results. It is the canonical
registry for behavior-affecting Code Wiki result choices.

## Registry

| Field | Allowed values | Default | Notes |
| --- | --- | --- | --- |
| `validation_status` | `pass`, `pass-with-warnings`, `fail` | Derived from errors and warnings | `fail` requires one or more errors; `pass-with-warnings` requires no errors and one or more warnings; `pass` requires neither. |

The validator emits `validation_status=<value>` as its first line. Human output
may render the same result as `PASS`, `PASS WITH WARNINGS`, or `FAIL`, but
callers branch only on `validation_status`. Error and warning messages remain
separate prose data.
