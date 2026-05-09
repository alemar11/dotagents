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
   - target kind: `skill`, `plugin`, or `bundled plugin skill`
   - observed strengths
   - missing or weak behavior
   - behavior evidence status: session-confirmed, summary-only, or no
     invocation evidence found
   - evidence source
   - highest-value next update
   - owning surface for the fix: `skill`, `bundled plugin skill`, `plugin`,
     or `docs`
4. `Add / merge / disable candidates`
   List only candidates justified by evidence after reviewing the audited
   scope.
5. `Priority order`
   Rank the top recommendations by expected value.
6. `Follow-up question`
   In full-portfolio audits where `skill-audit` was not explicitly requested,
   end by asking whether the user wants a follow-up audit of `skill-audit`
   too.
