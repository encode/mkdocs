from click.testing import CliRunner
import os
import mkdocs
import pathlib


def test_mkdocs_help():
    runner = CliRunner()
    result = runner.invoke(mkdocs.mkdocs, ['--help'])
    assert result.exit_code == 0
    assert result.output == (
        'Usage: mkdocs [OPTIONS] COMMAND [ARGS]...\n'
        '\n'
        'Options:\n'
        '  --help  Show this message and exit.\n'
        '\n'
        'Commands:\n'
        '  build\n'
        '  serve\n'
    )


def test_mkdocs_build(tmp_path: pathlib.Path):
    # Setup
    os.chdir(tmp_path)

    docs = tmp_path / "docs"
    docs.mkdir()

    readme = docs / "README.md"
    readme.write_text("# README\n\nhello world!\n")

    site = tmp_path / "site"

    homepage = site / "index.html"

    # Test
    runner = CliRunner()
    result = runner.invoke(mkdocs.mkdocs, ['build'])
    assert result.exit_code == 0
    assert result.output == (
        'Collected 1 resources\n'
        ' + README.md [markdown]\n'
    )
    assert site.exists()
    assert homepage.exists()
    assert "<p>hello world!</p>" in homepage.read_text()
