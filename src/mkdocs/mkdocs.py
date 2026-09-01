import click
import contextlib
import contextvars
import jinja2
import markdown
import pathlib
import posixpath
import shutil
import httpx


RED = '\033[31m'
GREEN = '\033[32m'
BOLD = '\033[1m'
LIGHT_GRAY = '\033[37m'
DARK_GRAY = '\033[90m'
RESET = '\033[0m'


# The build context is used to ensure the current page and the site index
# are available to the RelativeURLs markdown extension.
_current_page = contextvars.ContextVar('current_page')
_site_index = contextvars.ContextVar('site_index')


def get_current_page():
    ctx = _current_page.get()
    if ctx is None:
        raise RuntimeError("No current context")
    return ctx


def get_site_index():
    ctx = _site_index.get()
    if ctx is None:
        raise RuntimeError("No current context")
    return ctx


class Page:
    def __init__(self, path):
        self.path = path
        if path.name.lower() in ('readme.md', 'index.md'):
            # 'README.md' -> 'index.html'
            self.build_path = path.with_name('index.html')
        else:
            # 'topics/API.md' -> 'topics/api/index.html'
            self.build_path = path.with_name(path.stem.lower()).joinpath('index.html')
        # 'index.html' -> '/'
        # 'topics/api/index.html' -> '/topics/api/'
        url = pathlib.PosixPath('/').joinpath(self.build_path)
        self.url = str(url).removesuffix('index.html')


class PageContext:
    def __init__(self, page, title, html, toc):
        self.path = page.path
        self.url = page.url
        self.title = title
        self.html = html
        self.toc = toc


class Static:
    def __init__(self, path):
        self.path = path
        url = pathlib.PosixPath('/').joinpath(self.path)
        self.url = str(url).removesuffix('index.html')


class SiteIndex:
    def __init__(self, pages, statics):
        self._pages = pages
        self._statics = statics

        self.lookup = {
            str(resource.path): resource for resource in pages + statics
        }
        self.lookup_by_url = {
            str(resource.url): resource for resource in pages + statics
        }

    @property
    def pages(self) -> list[Page]:
        return list(self._pages)

    @property
    def statics(self) -> list[Static]:
        return list(self._statics)

    def __len__(self) -> int:
        return len(self.pages) + len(self.statics)


class MkDocs:
    def __init__(self, input_dir):
        self.site_index = self.load_site(input_dir)
        self.env = self.init_env(input_dir)
        self.md = self.init_md()
        self.base = self.env.get_template('base.html')

    def load_site(self, input_dir):
        dir = pathlib.Path(input_dir)
        paths = sorted([
            path.relative_to(dir)
            for path in dir.rglob("[!.]*")
            if path.is_file()
        ])

        pages = []
        statics = []

        for path in paths:
            if path.parts[0] == "templates":
                pass
            elif path.suffix == ".md":
                page = Page(path)
                pages.append(page)
            else:
                static = Static(path)
                statics.append(static)

        pages = sorted(pages, key=lambda x: x.url)
        statics = sorted(statics, key=lambda x: x.url)
        return SiteIndex(pages, statics)

    def init_env(self, input_dir) -> jinja2.Environment:
        @jinja2.pass_context
        def url(ctx, url_to):
            url_from = ctx['page'].url
            url_rel = posixpath.relpath(url_to, url_from)  # This isn't correct
            return url_rel

        dir = pathlib.Path(input_dir)
        loader = jinja2.ChoiceLoader([
            jinja2.FileSystemLoader(dir.joinpath("templates")),
            jinja2.PackageLoader('mkdocs', 'theme'),
        ])
        env = jinja2.Environment(loader=loader, auto_reload=True)
        env.filters['url'] = url
        return env

    def init_md(self) -> markdown.Markdown:
        return markdown.Markdown(
            extensions=[
                'fenced_code',
                'footnotes',
                'tables',
                'toc',
                # 'pymdownx.tasklist',
                # 'gfm_admonition',
                'mkdocs.extensions.relative_urls',
                'mkdocs.extensions.short_codes',
                'mkdocs.extensions.strike_thru',
            ],
            extension_configs={
                'footnotes': {'BACKLINK_TITLE': ''},
                'toc': {'anchorlink': True, 'marker': '', 'toc_class': ''}
            }
        )

    @contextlib.contextmanager
    def set_context(self, current_page):
        token_page = _current_page.set(current_page)
        token_site = _site_index.set(self.site_index)
        try:
            yield
        finally:
            _current_page.reset(token_page)
            _site_index.reset(token_site)

    def build(self, input, output):
        input_dir = pathlib.Path(input)
        output_dir = pathlib.Path(output)

        print(DARK_GRAY + "Collected %d resources" % len(self.site_index) + RESET)
        for page in self.site_index.pages:
            print(GREEN + " + " + RESET + BOLD + str(page.path) + RESET + DARK_GRAY + " [markdown]" + RESET)
            input_path = input_dir.joinpath(page.path)
            output_path = output_dir.joinpath(page.build_path)

            with self.set_context(page):
                text = input_path.read_text()
                html = self.md.reset().convert(text)
                title = self.md.toc_tokens[0]['name'] if self.md.toc_tokens else ''
                page_ctx = PageContext(page=page, title=title, html=html, toc=self.md.toc)
                output = self.base.render(page=page_ctx)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output)

        for static in self.site_index.statics:
            print(GREEN + " + " + RESET + BOLD + str(static.path) + RESET + DARK_GRAY + " [static]" + RESET)
            input_path = input_dir.joinpath(static.path)
            output_path = output_dir.joinpath(static.path)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(input_path, output_path)

    def serve(self, input):
        input_dir = pathlib.Path(input)

        print(DARK_GRAY + "Serving %d resources" % len(self.site_index) + RESET)
        for page in self.site_index.pages:
            print(GREEN + " + " + RESET + BOLD + str(page.url) + RESET + DARK_GRAY + " [markdown]" + RESET)
        for static in self.site_index.statics:
            print(GREEN + " + " + RESET + BOLD + str(static.url) + RESET + DARK_GRAY + " [static]" + RESET)
        print()

        def app(request):
            resource = self.site_index.lookup_by_url.get(request.url.path)

            if isinstance(resource, Page):
                input_path = input_dir.joinpath(resource.path)
                with self.set_context(resource):
                    text = input_path.read_text()
                    html = self.md.reset().convert(text)
                    title = self.md.toc_tokens[0]['name'] if self.md.toc_tokens else ''
                    page_ctx = PageContext(page=page, title=title, html=html, toc=self.md.toc)
                    output = self.base.render(page=page_ctx)
                return httpx.Response(200, content=httpx.HTML(output))
            elif isinstance(resource, Static):
                input_path = input_dir.joinpath(resource.path)
                return httpx.Response(200, content=httpx.File(input_path))
            return httpx.Response(404, content=httpx.Text("Not Found"))

        server = httpx.Server(app)
        server.serve()


@click.group()
def cli():
    if pathlib.Path('mkdocs.yml').exists():
        raise Exception('Found mkdocs.yml config, but mkdocs 2.0 pre-release is installed')


@cli.command()
@click.option('--dir', default='docs', help="Default 'docs'.", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output', default='site', help="Default 'site'.", type=click.Path(file_okay=False, dir_okay=True))
def build(dir, output):
    m = MkDocs(dir)
    m.build(dir, output)


@cli.command()
@click.option('--dir', default='docs', help="Default 'docs'.", type=click.Path(exists=True, file_okay=False, dir_okay=True))
def serve(dir):
    m = MkDocs(dir)
    m.serve(dir)
