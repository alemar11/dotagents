# Metadata Alignment

Use for metadata/docs-only maintenance or description review. Inspect only the
selected packages and their catalog/install mentions. A review reports proposed
corrections; an authorized edit aligns them. Do not expand this route into a
structural audit, domain refresh, or a new skill scaffold.

## Sources and boundaries

`SKILL.md` frontmatter owns the name, purpose, and trigger intent. Keep
`agents/openai.yaml` and README one-liners semantically aligned with it. Keep
workflow detail in the skill body or its conditional references. Preserve
invocation policy and unrelated dependency fields.

For behavior-sensitive trigger changes, first apply the criteria in
[instruction-density-review.md](instruction-density-review.md); do not assume
that a shorter description preserves selection behavior.

## UI fields

Use the canonical skill metadata validator and the current skill-creator
metadata reference when an unfamiliar field needs clarification. Existing UI
fields follow these constraints:

- `display_name` and `short_description` describe the public capability;
  the short description is 25–64 characters.
- `default_prompt` is a short example mentioning `$<skill-name>`.
- Icon paths resolve under the skill's `assets/` directory.
- Preserve explicit-only policy and unrelated dependencies. A new `brand_color`
  must be unused in the repository.

## Alignment pass

Compare the targeted frontmatter, UI fields, and README descriptions. For
plugins, also compare manifests and marketplace entries. Fix only authorized
mismatches, preserving purpose and scope. Reconcile changed identities in
catalogs, install prompts, and usage examples; do not invent entries for an
empty marketplace. New skills belong to their creator workflow, not this pass.

Return changed paths, preserved invocation policy, unresolved drift, and any
metadata validation already performed to the shared release checklist. It owns
final parsing and reference checks; metadata-only work does not require a
separate health audit.
