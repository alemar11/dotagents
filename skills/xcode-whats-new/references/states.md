# Xcode What's New State Contract

The helper derives transient selection state from the invocation and observes
release state from Apple's Xcode Release Notes index. It does not persist
runtime state or configuration.

## Selection mode

| Field | Allowed values | State kind | Meaning |
| --- | --- | --- | --- |
| `selection_mode` | `active`, `requested`, `list` | Transient | Resolve the selected local Xcode, one caller-supplied version label, or the complete Apple release-note index. |

## Release channel

| Field | Allowed values | State kind | Meaning |
| --- | --- | --- | --- |
| `release_channel` | `stable`, `beta` | External | Classify an Apple release-note title as a stable release or beta release. |
| `beta_iteration` | positive integer or absent | External | Preserve an explicitly numbered beta such as Beta 6; absence means the current beta for the requested major version. |

Beta iteration is matching metadata, not another release channel. Requested
stable and beta lookups must remain on their requested channel. A numbered beta
must match exactly. Active selection derives a beta channel from the selected
Xcode application's path because `xcodebuild` reports only the numeric version
and final Apple build identifiers can end in a lowercase letter.
