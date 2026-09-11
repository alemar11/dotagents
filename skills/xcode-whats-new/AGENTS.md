# Xcode What's New Maintenance

Keep runtime execution on `scripts/print_xcode_changelog.py`; there is no
separate build project or generated runtime artifact. The helper's `--version`
option selects an Xcode release, not a helper version.

After changing the helper, run its unit tests, `--help`, `--list`, an explicit
stable lookup, an explicit beta lookup, and the default active-Xcode report.
