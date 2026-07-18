# Project Layout

## Configuration

| Key | Type | Value | Allowed values | Meaning |
| --- | --- | --- | --- | --- |
| `repository_layout` | enum | `monorepo` | `single-repository`, `monorepo`, `multi-repository-workspace` | One Git repository contains independently planned reusable skills and repo-local plugins. |

Planning remains rooted in this repository. Individual skills and plugins may
own scoped Feature Specs without becoming separate repositories.
