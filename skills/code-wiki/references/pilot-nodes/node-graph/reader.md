# Final Reader Evaluation

| Field | Value |
| --- | --- |
| `node_id` | `reader` |
| `node_kind` | `agent-reader` |
| `dependencies` | `validate` |
| `input_artifacts` | `wiki`, `artifacts/validation.json` |
| `output_artifacts` | `artifacts/reader-evaluation.json` |
| `repair_target` | `none` |

## Instructions

Read the complete generated wiki as a new maintainer and apply this exact
reader contract without editing the wiki. Check required-page completeness,
navigation and local-link integrity, evidence fidelity against the source,
unsupported-claim risk, and material omissions. Write only
artifacts/reader-evaluation.json with these exact fields: reader_status using
pass or fail; required_page_completeness using pass or fail;
navigation_link_integrity using pass or fail; evidence_fidelity using pass or
fail; unsupported_claim_risk using none or material; material_omissions as an
array of concise strings; and summary as a nonempty string. Mark reader_status
fail when any component fails, risk is material, or material omissions exist.
