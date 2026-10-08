# Hosted Content Safety

Apply to every hosted specification artifact, including legacy task updates and
revision notes. Architect owns the content projection and bounded repair;
authenticated `gh` owns transport and readback.

Local paths, prompts, dialogue and tool output may inform the working context.
Hosted content includes only portable facts needed for its purpose. A temporary
body-file path is allowed as a private transport argument, never as hosted text.

## Portable projection and mandatory correction

Convert paths under the owning root to repository-relative paths with portable
separators. Represent locations outside it by known repository identity, branch,
full SHA and hosted references when available. Remove local absolute paths and
machine-specific locations; never guess replacements or invent identities.
Exclude irrelevant prompt machinery, host/task identity and transcript fragments.
Apply the same rules to copied worker, tool and provider content.

Preserve required evidence and semantics. If an optional local-only detail has
no portable representation, omit it and record an internal warning; that omission
alone does not require a question or block the workflow.

## Single-line title projection

Freeze the title as one non-empty semantic line. Preserve its exact UTF-8 bytes
in transport, removing only serialization-added final CR/LF, not meaningful
text. An interior line break requires reconstruction from the intended title,
not flattening unknown content. This rule does not alter body formatting.

## Final pre-write correction

Immediately before each write, inspect the exact final content against these
rules. Correct violations and repeat the full check after any content change.
Never submit a known local absolute path; required evidence must remain intact.

## Post-write readback and repair

Read back the exact hosted content after every create or update; this does not
replace the pre-write check. If it contains a local absolute or machine-specific
path, compute a compliant projection, make at most one correction to the same
artifact, and read it back again. Retain the repair outcome outside the spec.

Never replace the artifact or repeat an ambiguous or already attempted repair.
If repair is unavailable, fails, or remains ambiguous, report the exact artifact
and unresolved effect under [states.md](states.md). Publication is not complete
until conformity is verified; completed refinement and unaffected work may
proceed independently.
