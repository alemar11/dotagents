# Package Availability Checks

Use the package manager or registry that matches the repository.

## npm

```bash
npm view <package> version
npm view <package>@<version> dist.tarball
```

## PyPI

```bash
python3 -m pip index versions <package>
python3 -m pip install --dry-run <package>==<version>
```

## Homebrew

```bash
brew info <formula>
brew livecheck <formula>
```

## GitHub Packages

Use `gh api` against the package endpoint when package visibility or owner
scope matters. Report the endpoint and returned version or tag.
