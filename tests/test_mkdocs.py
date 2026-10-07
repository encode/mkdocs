from click.testing import CliRunner
import mkdocs


def test_mkdocs():
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
