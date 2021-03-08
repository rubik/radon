try:
    import collections.abc as collections_abc
except ImportError:
    import collections as collections_abc

import pytest

import radon.cli.harvest as harvest
import radon.complexity as cc_mod
from radon.cli import Config

BASE_CONFIG = Config(
    exclude=r'test_[^.]+\.py',
    ignore='tests,docs',
    include_ipynb=False,
    ipynb_cells=False,
)

CC_CONFIG = Config(
    order=getattr(cc_mod, 'SCORE'),
    no_assert=False,
    min='A',
    max='F',
    show_complexity=False,
    show_closures=False,
    average=True,
    total_average=False,
    **BASE_CONFIG.config_values
)

RAW_CONFIG = Config(summary=True,)

MI_CONFIG = Config(multi=True, min='B', max='C', show=True, sort=False,)


def fake_gobble(fobj):
    return 42


def fake_gobble_raising(fobj):
    raise TypeError('mystr')


def fake_run():
    for i in range(3):
        yield {'file-{0}'.format(i): i ** 2}


@pytest.fixture
def base_config():
    return Config(**BASE_CONFIG.config_values.copy())


@pytest.fixture
def cc_config():
    return Config(**CC_CONFIG.config_values.copy())


@pytest.fixture
def raw_config():
    return Config(**RAW_CONFIG.config_values.copy())


@pytest.fixture
def mi_config():
    return Config(**MI_CONFIG.config_values.copy())


def test_base_iter_filenames(base_config, mocker):
    iter_mock = mocker.patch('radon.cli.harvest.iter_filenames')
    h = harvest.Harvester([], base_config)
    h._iter_filenames()

    iter_mock.assert_called_with([], base_config.exclude, base_config.ignore)


def test_base_gobble_not_implemented(base_config):
    h = harvest.Harvester([], base_config)
    with pytest.raises(NotImplementedError):
        h.gobble(None)


def test_base_as_xml_not_implemented(base_config):
    h = harvest.Harvester([], base_config)
    with pytest.raises(NotImplementedError):
        h.as_xml()


def test_base_as_md_not_implemented(base_config):
    h = harvest.Harvester([], base_config)
    with pytest.raises(NotImplementedError):
        h.as_md()


def test_base_to_terminal_not_implemented(base_config):
    h = harvest.Harvester([], base_config)
    with pytest.raises(NotImplementedError):
        h.to_terminal()


def test_base_run(base_config):
    h = harvest.Harvester(['-'], base_config)
    h.gobble = fake_gobble
    assert isinstance(h.run(), collections_abc.Iterator)
    assert list(h.run()) == [('-', 42)]
    h.gobble = fake_gobble_raising
    assert list(h.run()) == [('-', {'error': 'mystr'})]


def test_base_results(base_config):
    h = harvest.Harvester([], base_config)
    h.run = fake_run
    results = h.results
    assert isinstance(results, collections_abc.Iterator)
    assert list(results) == [{'file-0': 0}, {'file-1': 1}, {'file-2': 4}]
    assert not isinstance(h.results, collections_abc.Iterator)
    assert isinstance(h.results, collections_abc.Iterable)
    assert isinstance(h.results, list)


def test_base_as_json(base_config):
    h = harvest.Harvester([], base_config)
    h._results = {'filename': {'complexity': 2}}
    assert h.as_json() == '{"filename": {"complexity": 2}}'


def test_cc_gobble(cc_config, mocker):
    sr_mock = mocker.patch('radon.cli.harvest.sorted_results')
    cc_mock = mocker.patch('radon.cli.harvest.cc_visit')
    cc_mock.return_value = []
    fobj = mocker.MagicMock()
    fobj.read.return_value = mocker.sentinel.one

    h = harvest.CCHarvester([], cc_config)
    h.config.show_closures = True
    h.gobble(fobj)

    assert fobj.read.called
    cc_mock.assert_called_with(
        mocker.sentinel.one, no_assert=cc_config.no_assert
    )
    sr_mock.assert_called_with([], order=cc_config.order)


def test_cc_to_dicts(cc_config, mocker):
    c2d_mock = mocker.patch('radon.cli.harvest.cc_to_dict')
    c2d_mock.side_effect = lambda i: i
    h = harvest.CCHarvester([], cc_config)
    sample_results = [
        ('a', [{'rank': 'A'}]),
        ('b', [{'rank': 'B'}]),
        ('c', {'error': 'An ERROR!'}),
    ]
    h._results = sample_results

    assert h._to_dicts() == dict(sample_results)
    assert c2d_mock.call_count == 2

    h.config.min = 'B'
    h._results = sample_results[1:]
    assert h._to_dicts() == dict(sample_results[1:])


def test_cc_as_json_xml(cc_config, mocker):
    d2x_mock = mocker.patch('radon.cli.harvest.dict_to_xml')
    to_dicts_mock = mocker.MagicMock()
    to_dicts_mock.return_value = {'a': {'rank': 'A'}}

    h = harvest.CCHarvester([], cc_config)
    h._to_dicts = to_dicts_mock
    assert h.as_json() == '{"a": {"rank": "A"}}'

    h.as_xml()
    assert d2x_mock.called
    d2x_mock.assert_called_with(to_dicts_mock.return_value)
    assert to_dicts_mock.call_count == 2


def test_cc_as_md(cc_config, mocker):
    d2md_mock = mocker.patch('radon.cli.harvest.dict_to_md')
    to_dicts_mock = mocker.MagicMock()
    to_dicts_mock.return_value = {'a': {'rank': 'A'}}

    h = harvest.CCHarvester([], cc_config)
    h._to_dicts = to_dicts_mock
    assert h.as_md()
    assert d2md_mock.called
    d2md_mock.assert_called_with(to_dicts_mock.return_value)
    assert to_dicts_mock.call_count == 1


def test_cc_to_terminal(cc_config, mocker):
    reset_mock = mocker.patch('radon.cli.harvest.RESET')
    ranks_mock = mocker.patch('radon.cli.harvest.RANKS_COLORS')
    c2t_mock = mocker.patch('radon.cli.harvest.cc_to_terminal')
    h = harvest.CCHarvester([], cc_config)
    h._results = [('a', {'error': 'mystr'}), ('b', {})]
    c2t_mock.return_value = (['res'], 9, 3)
    ranks_mock.__getitem__.return_value = '<|A|>'
    reset_mock.__eq__.side_effect = lambda o: o == '__R__'

    results = list(h.to_terminal())
    c2t_mock.assert_called_once_with(
        {},
        cc_config.show_complexity,
        cc_config.min,
        cc_config.max,
        cc_config.total_average,
    )
    assert results == [
        ('a', ('mystr',), {'error': True}),
        ('b', (), {}),
        (['res'], (), {'indent': 1}),
        ('\n{0} blocks (classes, functions, methods) analyzed.', (3,), {}),
        (
            'Average complexity: {0}{1} ({2}){3}',
            ('<|A|>', 'A', 3, '__R__'),
            {},
        ),
    ]


def test_raw_gobble(raw_config, mocker):
    r2d_mock = mocker.patch('radon.cli.harvest.raw_to_dict')
    analyze_mock = mocker.patch('radon.cli.harvest.analyze')
    fobj = mocker.MagicMock()
    fobj.read.return_value = mocker.sentinel.one
    analyze_mock.return_value = mocker.sentinel.two

    h = harvest.RawHarvester([], raw_config)
    h.gobble(fobj)

    assert fobj.read.call_count == 1
    analyze_mock.assert_called_once_with(mocker.sentinel.one)
    r2d_mock.assert_called_once_with(mocker.sentinel.two)


def test_raw_as_xml(raw_config):
    h = harvest.RawHarvester([], raw_config)
    with pytest.raises(NotImplementedError):
        h.as_xml()


def test_raw_to_terminal(raw_config):
    h = harvest.RawHarvester([], raw_config)
    h._results = [
        ('a', {'error': 'mystr'}),
        (
            'b',
            {
                'loc': 24,
                'lloc': 27,
                'sloc': 15,
                'comments': 3,
                'multi': 3,
                'single_comments': 3,
                'blank': 9,
            },
        ),
        (
            'c',
            {
                'loc': 24,
                'lloc': 27,
                'sloc': 15,
                'comments': 3,
                'multi': 3,
                'single_comments': 13,
                'blank': 9,
            },
        ),
        (
            'e',
            {
                'loc': 0,
                'lloc': 0,
                'sloc': 0,
                'comments': 0,
                'single_comments': 12,
                'multi': 0,
                'blank': 0,
            },
        ),
    ]

    assert list(h.to_terminal()) == [
        ('a', ('mystr',), {'error': True}),
        ('b', (), {}),
        ('{0}: {1}', ('LOC', 24), {'indent': 1}),
        ('{0}: {1}', ('LLOC', 27), {'indent': 1}),
        ('{0}: {1}', ('SLOC', 15), {'indent': 1}),
        ('{0}: {1}', ('Comments', 3), {'indent': 1}),
        ('{0}: {1}', ('Single comments', 3), {'indent': 1}),
        ('{0}: {1}', ('Multi', 3), {'indent': 1}),
        ('{0}: {1}', ('Blank', 9), {'indent': 1}),
        ('- Comment Stats', (), {'indent': 1}),
        ('(C % L): {0:.0%}', (0.125,), {'indent': 2}),
        ('(C % S): {0:.0%}', (0.2,), {'indent': 2}),
        ('(C + M % L): {0:.0%}', (0.25,), {'indent': 2}),
        ('c', (), {}),
        ('{0}: {1}', ('LOC', 24), {'indent': 1}),
        ('{0}: {1}', ('LLOC', 27), {'indent': 1}),
        ('{0}: {1}', ('SLOC', 15), {'indent': 1}),
        ('{0}: {1}', ('Comments', 3), {'indent': 1}),
        ('{0}: {1}', ('Single comments', 13), {'indent': 1}),
        ('{0}: {1}', ('Multi', 3), {'indent': 1}),
        ('{0}: {1}', ('Blank', 9), {'indent': 1}),
        ('- Comment Stats', (), {'indent': 1}),
        ('(C % L): {0:.0%}', (0.125,), {'indent': 2}),
        ('(C % S): {0:.0%}', (0.2,), {'indent': 2}),
        ('(C + M % L): {0:.0%}', (0.25,), {'indent': 2}),
        ('e', (), {}),
        ('{0}: {1}', ('LOC', 0), {'indent': 1}),
        ('{0}: {1}', ('LLOC', 0), {'indent': 1}),
        ('{0}: {1}', ('SLOC', 0), {'indent': 1}),
        ('{0}: {1}', ('Comments', 0), {'indent': 1}),
        ('{0}: {1}', ('Single comments', 12), {'indent': 1}),
        ('{0}: {1}', ('Multi', 0), {'indent': 1}),
        ('{0}: {1}', ('Blank', 0), {'indent': 1}),
        ('- Comment Stats', (), {'indent': 1}),
        ('(C % L): {0:.0%}', (0.0,), {'indent': 2}),
        ('(C % S): {0:.0%}', (0.0,), {'indent': 2}),
        ('(C + M % L): {0:.0%}', (0.0,), {'indent': 2}),
        ('** Total **', (), {}),
        ('{0}: {1}', ('LOC', 48), {'indent': 1}),
        ('{0}: {1}', ('LLOC', 54), {'indent': 1}),
        ('{0}: {1}', ('SLOC', 30), {'indent': 1}),
        ('{0}: {1}', ('Comments', 6), {'indent': 1}),
        ('{0}: {1}', ('Single comments', 28), {'indent': 1}),
        ('{0}: {1}', ('Multi', 6), {'indent': 1}),
        ('{0}: {1}', ('Blank', 18), {'indent': 1}),
        ('- Comment Stats', (), {'indent': 1}),
        ('(C % L): {0:.0%}', (0.125,), {'indent': 2}),
        ('(C % S): {0:.0%}', (0.2,), {'indent': 2}),
        ('(C + M % L): {0:.0%}', (0.25,), {'indent': 2}),
    ]


def test_mi_gobble(mi_config, mocker):
    mv_mock = mocker.patch('radon.cli.harvest.mi_visit')
    fobj = mocker.MagicMock()
    fobj.read.return_value = mocker.sentinel.one
    mv_mock.return_value = 23.5

    h = harvest.MIHarvester([], mi_config)
    result = h.gobble(fobj)

    assert fobj.read.call_count == 1
    mv_mock.assert_called_once_with(mocker.sentinel.one, mi_config.multi)
    assert result == {'mi': 23.5, 'rank': 'A'}


def test_mi_as_json(mi_config, mocker):
    d_mock = mocker.patch('radon.cli.harvest.json.dumps')
    h = harvest.MIHarvester([], mi_config)
    h.config.min = 'C'
    h._results = [
        ('a', {'error': 'mystr'}),
        ('b', {'mi': 25, 'rank': 'A'}),
        ('c', {'mi': 15, 'rank': 'B'}),
        ('d', {'mi': 0, 'rank': 'C'}),
    ]

    h.as_json()
    d_mock.assert_called_with(dict([h._results[0], h._results[-1]]))


def test_mi_as_xml(mi_config):
    h = harvest.MIHarvester([], mi_config)
    with pytest.raises(NotImplementedError):
        h.as_xml()


def test_mi_to_terminal(mi_config, mocker):
    reset_mock = mocker.patch('radon.cli.harvest.RESET')
    ranks_mock = mocker.patch('radon.cli.harvest.MI_RANKS')
    ranks_mock.__getitem__.side_effect = lambda j: '<|{0}|>'.format(j)
    reset_mock.__eq__.side_effect = lambda o: o == '__R__'

    h = harvest.MIHarvester([], mi_config)
    h._results = [
        ('a', {'error': 'mystr'}),
        ('b', {'mi': 25, 'rank': 'A'}),
        ('c', {'mi': 15, 'rank': 'B'}),
        ('d', {'mi': 0, 'rank': 'C'}),
    ]

    assert list(h.to_terminal()) == [
        ('a', ('mystr',), {'error': True}),
        ('{0} - {1}{2}{3}{4}', ('c', '<|B|>', 'B', ' (15.00)', '__R__'), {}),
        ('{0} - {1}{2}{3}{4}', ('d', '<|C|>', 'C', ' (0.00)', '__R__'), {}),
    ]
