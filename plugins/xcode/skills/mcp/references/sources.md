# Xcode MCP Sources

Use these sources to verify provenance or investigate command drift. Always
confirm the selected installation's live `mcp-server` help before execution.

## Apple documentation

- [Giving external agents access to Xcode](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode)
  documents Apple's native Xcode MCP integration for external agents.
- [Xcode 27 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes)
  introduced the headless `mcp-server` preview and states that unsafe global
  agent approval is not recommended for at-desk use.

## X follow-up correction

- [Julian Schiavo's complete X thread](https://x.com/_julianschiavo/status/2086880132640428080)
  must be read with its follow-ups, not as only the initial post. The follow-up
  corrects normal setup to use standard enablement and start, followed by
  approval of the verified signed agent. It reserves unsafe global approval for
  isolated unattended or CI environments.

Treat the X thread as useful practitioner context, not as authority over the
selected Xcode's live help or current Apple documentation.
