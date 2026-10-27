# Command Line Interface

## Commands

MkDocs is used entirely from the command line. At this stage of the pre-release, there are two commands available:

### `mkdocs build`

Builds your documentation into a static site - a folder of HTML files you can host anywhere.

```shell
mkdocs build
```

By default, this reads your source files from `docs/` and writes the generated site to `site/`. You can change either location:

```shell
mkdocs build --dir SOURCE_DIRECTORY --output OUTPUT_DIRECTORY
```

**Note:** The list `mkdocs build` shows the source files it read, not the HTML files it generated - the build itself still completes correctly. ([Tracked as issue #61.](https://github.com/encode/mkdocs/issues/61))

### `mkdocs serve`

Starts a local development server so you can preview your site in a browser before publishing it.

```shell
mkdocs serve
```

By default, this serves your site at `http://127.0.0.1:8080`. Press `Ctrl+C` to stop it.

Like `build`, you can change the source directory:

```shell
mkdocs serve --dir SOURCE_DIRECTORY
```

There's currently no option to change the address or port `serve` runs on. If something else on your machine is already using port 8080, you'll need to free it up first.

**Note:** `serve` does not currently watch your files for changes - editing and saving a doc while the server is running does not trigger a rebuild or refresh the browser automatically. You'll need to refresh your browser manually, to see your latest edits.