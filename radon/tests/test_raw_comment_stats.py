import io

import pytest

from radon.cli.harvest import RawHarvester
from radon.cli import Config
from radon.metrics import mi_parameters
from radon.raw import analyze


@pytest.mark.parametrize(
    'docstring',
    [
        '"Short documentation."',
        "'Short documentation.'",
        '"""Short documentation."""',
        "'''Short documentation.'''",
    ],
)
def test_single_line_docstring_is_included_in_comments(docstring):
    result = analyze(docstring + '\nvalue = 1  # trailing comment\n')
    assert result.comments == 2
    assert result.single_comments == 1
    assert result.multi == 0
    assert (
        result.loc
        == result.sloc + result.single_comments + result.multi + result.blank
    )


def test_comment_statistics_include_each_kind_once():
    source = (
        '"""Module documentation."""\n# Comment\n'
        'value = 1  # Inline\n"""Long\ntext"""\n'
    )
    harvester = RawHarvester([], Config(summary=False, exclude='', ignore=''))
    metrics = harvester.gobble(io.StringIO(source))
    assert metrics['comments'] == 3
    assert metrics['single_comments'] == 2
    assert metrics['multi'] == 2
    harvester._results = [('example.py', metrics)]
    stats = {label: args for label, args, _ in harvester.to_terminal()}
    assert stats['(C % L): {0:.0%}'] == (3.0 / 5,)
    assert stats['(C % S): {0:.0%}'] == (3.0,)
    assert stats['(C + M % L): {0:.0%}'] == (1.0,)


@pytest.mark.parametrize('count_multi', [False, True])
def test_maintainability_includes_single_line_docstrings(count_multi):
    source = 'def function():\n    """Short documentation."""\n    return 42\n'
    assert mi_parameters(source, count_multi)[3] == 50.0


def test_assigned_strings_are_still_code():
    result = analyze('value = """This is data."""\n')
    assert result.comments == result.single_comments == result.multi == 0
    assert result.sloc == result.loc == 1
