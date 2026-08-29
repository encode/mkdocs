# MkDocs

MkDocs is a smart, simple, website design tool.

Getting started is easy...

```shell
$ pip install mkdocs --pre
```

*This will install the version 2.0 pre-release.*

## Getting started

1. Create a `docs/README.md` page.
2. Run `mkdocs serve` to view your documentation in a browser.
3. Run `mkdocs build` to build a static website ready to host.

## Writing your docs

1. Create additional markdown pages.
2. Use relative interlinking between pages.
3. Include images and use relative interlinking from pages.

*MkDocs supports [GitHub Flavored Markdown](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax) for page authoring.*

## Styling your docs

1. Create a `templates/base.html` to customise the styling.
2. Include css and javascript to serve static files.

*MkDocs uses [Jinja templating](https://jinja.palletsprojects.com/en/stable/templates/) for HTML rendering.*

A starting point can be as simple as...

```html
<html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ page.title }}</title>
        <link rel="stylesheet" href="{{ '/css/default.css' | url }}">
    </head>
    <body>
        <main>
            {{ page.html }}
        </main>
    </body>
</html>
```
