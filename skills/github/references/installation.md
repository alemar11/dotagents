# Git and GitHub CLI Setup

Confirm local tools:

```bash
command -v git && git --version
command -v gh && gh --version
gh auth status
```

Install GitHub CLI from the official project instructions:

- <https://github.com/cli/cli#installation>
- <https://github.com/cli/cli/releases/latest>

Authenticate before writes:

```bash
gh auth login
gh auth status
```
