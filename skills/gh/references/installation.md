# Installing GitHub CLI

Read this only when `gh` is missing or the user requests installation guidance.
Identify the execution environment with `uname -s`; on Linux inspect
`/etc/os-release` and the available package manager. Present only the matching
installation route. These commands are suggestions, not permission to run them.

## macOS

If Homebrew is already available, suggest:

```sh
brew install gh
```

If Homebrew is absent, offer the official precompiled binary for the machine's
architecture, or Homebrew setup if the user prefers it. Do not install a package
manager as an incidental prerequisite.

Source: [official macOS installation guide](https://github.com/cli/cli/blob/trunk/docs/install_macos.md).

## Linux

Prefer GitHub's official package repositories. For Debian and Ubuntu, include
the repository setup when absent; do not assume the distribution's `gh` package
is current. Check existing repository configuration before suggesting changes.

### Debian, Ubuntu, and Raspberry Pi OS

If the official GitHub CLI apt repository is not configured, suggest:

```sh
(command -v wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
  && sudo mkdir -p -m 755 /etc/apt/keyrings \
  && gh_keyring=$(mktemp) \
  && wget -nv -O "$gh_keyring" https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  && sudo install -m 644 "$gh_keyring" /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && rm "$gh_keyring" \
  && sudo mkdir -p -m 755 /etc/apt/sources.list.d \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list >/dev/null \
  && sudo apt update \
  && sudo apt install gh -y
```

If the official repository is already configured, only suggest:

```sh
sudo apt update && sudo apt install gh
```

### Fedora and other DNF distributions

Check `dnf --version`; DNF4 and DNF5 use different repository setup syntax.
Skip repository setup when the official GitHub CLI repository already exists.

For DNF5:

```sh
sudo dnf install dnf5-plugins
sudo dnf config-manager addrepo --from-repofile=https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install gh
```

For DNF4:

```sh
sudo dnf install 'dnf-command(config-manager)'
sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install gh
```

### Other Linux environments

If Homebrew is already the chosen package manager, `brew install gh` also works
on Linux. Otherwise use the matching route in the official Linux guide, or the
official precompiled release for the machine's architecture when package-manager
installation is unsuitable. Do not invent a distro command or add another
package manager just to install `gh`.

Source: [official Linux installation guide](https://github.com/cli/cli/blob/trunk/docs/install_linux.md).

## After installation

Verify `gh --version`. Check authentication for the target host with
`gh auth status --hostname <host>`. If login is needed, suggest
`gh auth login --hostname <host>`; use `github.com` for public GitHub and the
repository's host for GitHub Enterprise. Starting login still requires user
authorization. Resume the original GitHub task once the CLI is available and
the required access works.
