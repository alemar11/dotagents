# Spec Maintenance

The specification skill lives in `skills/spec/`. This directory holds only its
maintenance checks; it is not an installable skill or runtime dependency.

Run `scripts/validate-hosted-content-safety` after changing specification
publication content, templates, or their policy links. It resolves the skill
from this checkout and never edits installed copies.
