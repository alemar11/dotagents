# GitHub CLI setup for `ghops`

## Check whether `gh` is installed

```bash
command -v gh && gh --version
```

If `command -v gh` returns a path and `gh --version` prints output, the CLI is installed.

## Install GitHub CLI by OS

Prefer the official GitHub CLI install docs:

- Install guide: <https://github.com/cli/cli#installation>
- Latest release downloads: <https://github.com/cli/cli/releases/latest>
- Linux package instructions: <https://github.com/cli/cli/blob/trunk/docs/install_linux.md>

### macOS

Official:

```bash
brew install gh
```

Also supported on macOS:

```bash
sudo port install gh
```

Or download the universal installer or archives from the releases page.

### Windows

Official:

```powershell
winget install --id GitHub.cli
```

Community alternatives:

```powershell
choco install gh
```

```powershell
scoop install gh
```

Or download the `.msi` or `.exe` installer from the releases page. After install, open a new terminal window so `PATH` refreshes.

### Linux

#### Debian, Ubuntu, Raspberry Pi OS

Official:

```bash
(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
  && sudo mkdir -p -m 755 /etc/apt/keyrings \
  && out=$(mktemp) && wget -nv -O"$out" https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  && cat "$out" | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
  && sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && sudo mkdir -p -m 755 /etc/apt/sources.list.d \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
  && sudo apt update \
  && sudo apt install gh -y
```

#### Fedora, RHEL, CentOS, Amazon Linux, openSUSE, SUSE

Official DNF5:

```bash
sudo dnf install dnf5-plugins
sudo dnf config-manager addrepo --from-repofile=https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install gh --repo gh-cli
```

Official DNF4:

```bash
sudo dnf install 'dnf-command(config-manager)'
sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install gh --repo gh-cli
```

Amazon Linux 2 with `yum`:

```bash
type -p yum-config-manager >/dev/null || sudo yum install yum-utils
sudo yum-config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
sudo yum install gh
```

openSUSE or SUSE with `zypper`:

```bash
sudo zypper addrepo https://cli.github.com/packages/rpm/gh-cli.repo
sudo zypper ref
sudo zypper install gh
```

If Homebrew is already installed on Linux:

```bash
brew install gh
```

Or download the precompiled archive from the releases page.

## Authenticate

```bash
gh auth login
gh auth status
```

Use `gh auth status` to confirm the session before running write operations.

## Check `ghops` readiness before operations

```bash
ghops --json doctor
```

Use `--allow-non-project` only on `ghops` commands that explicitly support
non-project workflows.
