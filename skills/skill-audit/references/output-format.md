# Skill Audit Output Format

Use this structure for audits produced by `skill-audit`. Keep it compact,
decision-oriented, and evidence-backed.

1. `Audited targets`
   List the audited targets and the role each one plays.
2. `Evidence summary`
   Summarize the strongest repo, memory, session, cache-verification, and
   live-context signals that informed the audit.
3. `Per-target update roadmap`
   For each audited target, include:
   - target name
   - target kind: `standalone-skill`, `plugin-package`, or
     `bundled-plugin-skill`
   - observed strengths
   - missing or weak behavior
   - behavior evidence status: session-confirmed, summary-only, or no
     invocation evidence found
   - evidence source
   - writing-style diagnosis when `references/writing-style-review.md` changes
     prioritization or clarifies the fix
   - highest-value next update
   - owning surface for the fix: `standalone-skill`, `bundled-plugin-skill`,
     `plugin-package`, or `docs`
4. `Add / merge / disable candidates`
   List only candidates justified by evidence after reviewing the audited
   scope.
5. `Priority order`
   Rank the top recommendations by expected value.
6. `Follow-up question`
   In full-portfolio audits where `skill-audit` was not explicitly requested,
   end by asking whether the user wants a follow-up audit of `skill-audit`
   too.

## Live Monitor Format

For live monitoring, use a compact rolling report instead of the historical
roadmap above:

1. `Monitored tasks`
   List task identity, status, repository, and confirmed used surfaces.
2. `Performance snapshot`
   Summarize contract-compliant behavior, current phase, and evidence gaps.
3. `Defect annotations`
   List the complete stable `LIVE-NNN` registry with status, severity, owner,
   expected contract pointer, observed task evidence, impact, and remediation.
4. `Terminal assessment`
   After authoritative terminal reads, assess each used target separately and
   distinguish target defects from external runtime or repository conditions.

During the run, emit only material changes and bounded liveness updates. Never
report inferred progress or inferred defects when current task evidence is
unavailable.
