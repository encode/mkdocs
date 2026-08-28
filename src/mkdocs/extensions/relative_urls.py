import markdown
import mkdocs
import os
import posixpath
import httpx


class URLProcessor(markdown.treeprocessors.Treeprocessor):
    def run(self, root):
        page = mkdocs.get_current_page()
        site_index = mkdocs.get_site_index()
        key = ''
        link = ''

        for el in root.iter():
            # We want to rewrite image and links.
            if el.tag == 'a':
                key = 'href'
                link = el.get(key)
            elif el.tag == 'img':
                key = 'src'
                link = el.get(key)
            else:
                key = ''
                link = ''

            if link:
                el.set(key, link)
                url = httpx.URL(link)
                # We want to rewrite relative links... '/page'
                # We don't want to rewrite external links. 'https://elsewhere.com/here'
                # We don't want to rewrite anchor links. '#section'
                if url.is_relative_url and url._uri_reference.path:
                    path_from = page.path
                    path_to = os.path.normpath(path_from.parent.joinpath(url.path))

                    target = site_index.lookup.get(path_to)
                    if target is None:
                        continue  # Broken link!

                    url_from = page.url
                    url_to = target.url
                    rewrite = posixpath.relpath(url_to, url_from)
                    if url_to.endswith('/') and rewrite != '.':
                        rewrite += '/'
                    if url.query:
                        rewrite += f'?{url.query}'
                    if url.fragment:
                        rewrite += f'#{url.fragment}'
                    el.set(key, rewrite)


class RelativeURLs(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(URLProcessor(md), 'relative_urls', 15)


def makeExtension(**kwargs):
    return RelativeURLs(**kwargs)
