## Requirements

This guide uses uv, a fast Python package and project manager, to install and manage MkDocs and its dependencies. MkDocs 2.0's pre-release currently requires Python 3.10 or later — uv can fetch a suitable Python version for you automatically, so you don't need one already on your system.

You can check if you already have uv installed from the command line:

```shell
uv --version
```

If uv is installed, this prints a version number (something like `uv 0.12.13 ...`). If instead you see something like `command not found: uv`, follow the steps below to install it.

### Installing uv

Install uv using the standalone installer:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

If `uv` isn't recognized as a command right after installing, load it into your current shell session:

```shell
source $HOME/.local/bin/env
```

## Installing MkDocs

Install the mkdocs package using uv, allowing pre-release versions:

```shell
uv tool install mkdocs --prerelease allow
```

Note: this is *not* the same as pip's `--pre` flag — uv doesn't recognize `--pre` as a prerelease toggle at all, and will silently install the latest stable release instead, with no warning.

Verify what actually got installed:

```shell
uv tool list
```

This should show `mkdocs` at a `2.0.dev` version. If it shows an older `1.x` version instead, it's because uv didn't have a Python 3.10+ interpreter available to use for it. Check what uv has:

```shell
uv python list
```

If nothing 3.10 or newer shows as already installed (rather than just "download available"), fetch one (any version 3.10 or later — 3.12 is used here as the example):

```shell
uv python install 3.12
```

Then install again, specifying that interpreter directly:

```shell
uv tool install mkdocs --prerelease allow --python 3.12
```

Run `uv tool list` again to confirm.