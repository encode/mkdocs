import pathlib
import tomllib

import click
import mkdocs
import flask


CONTENT_TYPES = {
    ".json": "application/json",
    ".js": "application/javascript",
    ".html": "text/html",
    ".css": "text/css",
    ".png": "image/png",
    ".jpeg": "image/jpeg",
    ".jpg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
}


def default_config() -> dict:
    return {
        'mkdocs': {
            'nav': [],
        },
        'loaders': {
            'theme': 'pkg://mkdocs/default',
            'docs': 'dir://',
        },
        'context': {
        },
        'markdown': {
            'extensions': [
                'fenced_code',
                'footnotes',
                'tables',
                'toc',
                # 'pymdownx.tasklist',
                # 'gfm_admonition',
                'mkdocs.extensions.rewrite_urls',
                'mkdocs.extensions.short_codes',
                'mkdocs.extensions.strike_thru',
            ],
            'configs': {
                'footnotes': {'BACKLINK_TITLE': ''},
                'toc': {'anchorlink': True, 'marker': ''}
            },
        },
        # 'commands': {
        #     'build': 'mkdocs:build',
        #     'serve': 'mkdocs:serve',
        # }
    }


def load_config(path: pathlib.Path) -> dict:
    # Read the mkdocs.toml
    text = path.read_text()
    config = tomllib.loads(text)

    # Merge the default config.
    default = default_config()
    for key, value in default.items():
        if key not in config:
            config[key] = value

    return config


def build(mk: mkdocs.MkDocs) -> None:
    buildpath = pathlib.Path('site')
    for resource in mk.resources:
        output = mk.render(resource)
        build_path = buildpath.joinpath(resource.output_path)
        build_path.parent.mkdir(parents=True, exist_ok=True)
        build_path.write_bytes(output)


def serve(mk: mkdocs.MkDocs) -> None:
    urls = {resource.url: resource for resource in mk.resources}
    app = flask.Flask(__name__)

    @app.route("/")
    @app.route("/<path:path>")
    def _(path=''):
        # path = flask.request.url.path
        resource = urls.get(f"/{path}")
        if resource is None:
            redirect = f"/{path}/"
            if urls.get(redirect) is not None:
                # return flask.redirect(redirect)
                return flask.Response(status=302, headers={'Location': redirect})
            # not_found = httpx.Text('Not Found')
            text = 'Not Found'
            return flask.Response(text, status=404)
            # return flask.make_response(not_found, 404)
        content = mk.render(resource)
        content_type = CONTENT_TYPES.get(resource.output_path.suffix)
        return flask.Response(content, status=200, headers={'Content-Type': content_type})

    app.run()


def cli():
    path = pathlib.Path('mkdocs.toml')
    if path.exists():
        config = load_config(path)
    else:
        config = default_config()

    mk = mkdocs.MkDocs(config)
    group = click.Group(commands=[
        click.Command(name='build', callback=lambda: build(mk)),
        click.Command(name='serve', callback=lambda: serve(mk)),
    ])
    return group()
