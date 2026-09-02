# GitHub Actions configuration preflight

Detailed instructions for authoring the release workflow are not currently
present. This reference defines only the required preflight and the minimum
permissions contract. The preflight is advisory: it warns about a missing
repository setting but does not prevent the skill from writing a workflow that
the user explicitly requested.

## Repository setting

Before creating an Action that opens or approves pull requests, verify the
repository setting in GitHub:

1. Open the repository's **Settings**.
2. Open **Actions → General**.
3. Scroll to **Workflow permissions**.
4. Enable **Allow GitHub Actions to create and approve pull requests**.
5. Press **Save**.

If the option is missing or disabled, the Action can still be written when the
user authorized that change, but its PR-creation or PR-approval step will not
work until the setting is enabled. Do not try to work around the setting in the
workflow. It may be restricted by the GitHub plan/account or by an organization
or enterprise policy.

The official GitHub guidance is [Managing GitHub Actions settings for a
repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository#preventing-github-actions-from-creating-or-approving-pull-requests).

## Workflow permissions

The workflow must declare the minimum permissions needed by the job:

```yaml
permissions:
  contents: read
  pull-requests: write
```

If the Action also creates a branch or tag, use `contents: write` for the
scope that performs that operation:

```yaml
permissions:
  contents: write
  pull-requests: write
```

Prefer job-level permissions when only one job needs the write capability.
`default_workflow_permissions: write` is a repository default; it is not a
substitute for reviewing the workflow's explicit `permissions` declaration.

## Read-only CLI preflight

The shared G CLI can inspect the repository-level Actions settings before a
workflow is created:

```bash
<skill-root>/scripts/g --json ci permissions --repo <owner/repo> --allow-non-project
```

From a checkout with a matching `origin`, `--repo` and
`--allow-non-project` may be omitted:

```bash
<skill-root>/scripts/g --json ci permissions
```

The command reads these official REST endpoints through `gh api`:

- `GET /repos/{owner}/{repo}/actions/permissions`: whether Actions is enabled;
- `GET /repos/{owner}/{repo}/actions/permissions/workflow`: the default
  workflow permission level and `can_approve_pull_request_reviews`.

The result reports the repository gate for pull-request automation, but it
cannot prove the effective `pull-requests: write` token permission of a
workflow that has not run. The workflow YAML and, when necessary, a completed
run remain authoritative for that check. A forbidden response can mean the
authenticated `gh` token lacks the required Administration read permission,
or that an account, plan, organization, or enterprise policy prevents access.
If the result is blocked or unavailable and the user asked to create the
workflow, report the warning, write the requested Action with the documented
`permissions` block, and mark the workflow as pending repository configuration;
do not report the Action as functional until the setting is rechecked.

The [official GitHub Actions permissions REST API
documentation](https://docs.github.com/en/rest/actions/permissions?apiVersion=2022-11-28)
defines the endpoint and its response fields. The CLI uses the read-only
surface documented by [`gh api`](https://cli.github.com/manual/gh_api); it does
not call the corresponding `PUT` settings endpoints.

## Mutation boundary

This preflight never changes repository settings, workflow files, branches, or
tags. Changing the repository setting, adding a workflow, creating a branch,
creating a tag, or opening a pull request are separate mutations and require
explicit user authorization.
