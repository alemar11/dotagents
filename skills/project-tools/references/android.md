# Android

Install the official [android/skills](https://github.com/android/skills)
collection with the `skills` CLI through `npx`. Android CLI and Android Studio
are not prerequisites for installing these instruction files. The `android`
executable is a host-level tool; the `android-cli` skill is repository-local
content that explains how to install and use it later. Do not execute the
installed skill's host-setup instructions as part of this workflow.

## Prerequisites and scope

Check that `npx` is available. Missing Node.js/npm is a host prerequisite to
report, not install here. Run from the target repository root. Installation is
project-local by default; never pass `--global` or `-g`.

Select only the requested clients using `--agent`: `codex`, `cursor`, `pi`, or
`claude-code`. For multiple clients, pass their identifiers after `--agent`.
Use the [client destinations](../SKILL.md#clients) and inspect the installer's
actual paths. Keep any generated links inside the repository and preserve
existing custom skills and unrelated configuration.

## Discover and install

List the upstream collection without installing it:

```sh
npx --yes skills add android/skills --list
```

Use `--skill '*'` for the complete collection and an explicit agent selection.
This example installs for Pi; substitute the requested client:

```sh
npx --yes skills add android/skills --skill '*' --agent pi --yes
```

Only when all four clients are requested:

```sh
npx --yes skills add android/skills --skill '*' --agent codex cursor pi claude-code --yes
```

Do not use `skills add --all`: that selects all agents as well as all skills.
Before installation, compare the discovered names against existing project
skills. Preserve custom or locally modified collisions unless replacement is
already authorized; install unaffected names explicitly when needed. Skip
already-current copies rather than overwriting them routinely.

`gh skill install android/skills --all` did not discover Google's nested layout
when checked with gh 2.102.0. Use `npx skills` here rather than adding a dependency
on `android skills add` or maintaining a hardcoded upstream skill catalog.

## Update

Identify installed skills whose source is `android/skills` from project source
tracking. Update only those names, with explicit project scope. For example:

```sh
npx --yes skills update android-cli --project --yes
```

Pass the other installed Android skill names as additional positional arguments
when updating the collection. Never run a bare update that includes unrelated
project skills or can choose global scope. Check the affected destinations and
local modifications first; retain existing version pins unless changing them
is requested. If prior installations lack source tracking, reconcile their
provenance before reinstalling the same names from `android/skills`.

Updating installed names does not install newly published skills; use the
installation workflow when expanding or refreshing the full collection is
requested.

## Verification

List the project installation for the requested clients:

```sh
npx --yes skills list --agent pi
```

Inspect the skill files, source tracking, actual destinations, and scoped Git
diff. Report installed or updated names and unresolved conflicts. Preserve
upstream content apart from installer-managed metadata. File installation does
not prove that the active client has reloaded the skills or that the Android
executable is installed. Verify client discovery separately when requested;
for Pi, reload the session with `/reload` first.

## Sources

- [Official Android skills](https://github.com/android/skills)
- [Skills CLI installation and updates](https://github.com/vercel-labs/skills#readme)
