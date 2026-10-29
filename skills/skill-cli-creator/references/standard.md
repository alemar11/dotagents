# Skill CLI Standard

This file owns the standard every skill that ships a CLI follows, whether Claude
Code or Codex runs it. Other references and the template link here instead of
repeating it. `scripts/skill-cli-creator --json check <skill-dir>` verifies the
parts a program can check; the rest is review.

## Layout

```text
<skill>/
  SKILL.md                when to use the skill, the main commands, the rules
  AGENTS.md               maintenance: owned surfaces, version source, validation
  agents/openai.yaml      discovery metadata for Codex
  references/cli.md       every command, its JSON shape, and the exit codes
  references/states.md    only when the JSON carries status fields
  scripts/<skill>         the only runnable artifact
  tests/test_<module>.py  tests that run scripts/<skill>
  projects/<skill>/       only for a compiled or multi-file build; see compiled.md
```

- The artifact is named after the skill: `scripts/<skill>`, no extension. It is
  executable and starts with a shebang. A helper the artifact imports or calls
  may sit beside it, but agents and docs run only `scripts/<skill>`.
- `<module>` is the skill name with `-` replaced by `_`.
- The artifact is Python using the standard library, unless the job needs a
  compiled runtime; then follow [compiled](compiled.md).
- Commands run from the skill root: `scripts/<skill> ...`. A skill used from
  another repository says so: "from the skill root, run ...".

## Documents

- `SKILL.md` follows the [Agent Skills specification](https://agentskills.io/specification):
  `name` equals the directory name, `description` says what the skill does and
  when to use it in at most 1024 characters. Its body names the commands for
  the common jobs and the rules that change decisions (what needs the user's
  approval, what never to do), then links `references/cli.md` for the rest.
  It does not repeat option lists or JSON shapes.
- `references/cli.md` owns the command surface: each command with an example,
  its success payload fields, error codes, and exit codes.
- `references/states.md` exists only when results carry status fields such as
  `result_state`; it lists each value and what to do with it.
- `AGENTS.md` lists the owned surfaces, names `VERSION` as the version source,
  and gives the validation commands from [Validation](#validation).
- No per-skill `CLAUDE.md`: Claude Code reads the repository root `CLAUDE.md`,
  which imports `AGENTS.md`.

## Command line

- Global options come before the command: `scripts/<skill> [--json] <noun> <verb> [args]`.
- Commands are a product noun then a verb: `videos search`, `transcripts get`,
  `profiles list`. A noun alone is fine when it is the whole job (`doctor`).
- `--help` lists every command with one line each.
- `--version` prints `<skill> <x.y.z>` and exits 0.
- `doctor` reports readiness: the version, the runtime, each dependency, and
  missing setup. It writes nothing, never needs the network or credentials to
  run, and exits 0 even when something is missing. Its `ok` says whether the
  skill is ready, and the payload names what is missing.
- Options with a fixed set of values use lower-kebab values. Machine-readable
  field names are `snake_case`.
- Reads and `doctor` never write configuration. Configuration is written only
  by an explicit `init`, `login`, or `configure` command; see
  [compiled](compiled.md#configuration) for where it lives.

## JSON output

With `--json`, stdout carries exactly one JSON object and nothing else.
Progress and diagnostics go to stderr.

Success:

```json
{ "ok": true, "command": "videos search", "...": "command fields" }
```

Failure, for every error including invalid arguments:

```json
{ "ok": false, "command": "videos search", "error": { "code": "invalid-arguments", "message": "..." } }
```

- `command` is the noun and verb as typed, or `parse` when the arguments did
  not parse.
- `error.code` is lower-kebab and stable; `references/cli.md` lists each one.
- `doctor` always prints `ok`, `command: "doctor"`, and `version`, equal to
  what `--version` prints. It is the one command whose `ok: false` comes
  without an `error`: the missing pieces are in its own fields.
- Never print credentials, tokens, cookies, or private headers.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | The command did its job, including an empty result. |
| 1 | The command ran and failed: a check found problems, a request failed, a file was missing. |
| 2 | Invalid arguments. |
| 3 and up | Skill-specific failures, each listed in `references/cli.md`. |

A result that reports problems (a validator finding errors) exits nonzero and
uses the failure shape, with the details in extra fields.

## Version

`VERSION = "x.y.z"` in the artifact is the only source of the version; for a
compiled CLI, the build manifest is. Major for a breaking change to commands,
options, JSON fields, or exit codes; minor for a compatible capability; patch
for a fix. Doc-only changes do not bump it.

## Validation

Run after any change to the artifact:

```bash
python3 -m unittest discover -s tests
scripts/<skill> --help
scripts/<skill> --version
scripts/<skill> --json doctor
<path-to>/skill-cli-creator/scripts/skill-cli-creator --json check .
```

Add one safe end-to-end check for the skill's kind: an offline fixture for a
local tool, a read-only call for an API. Never a live write when a fixture
proves the behavior.

Tests run `scripts/<skill>` as a subprocess and assert behavior: exit codes,
JSON fields, files written. They do not assert prose or private helper names.
