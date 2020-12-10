import os
import sys
from configparser import ConfigParser

import pytest

import radon.cli as cli
import radon.complexity as cc_mod
from radon.cli.harvest import CCHarvester, Harvester, MIHarvester, RawHarvester
from radon.tests.test_cli_harvest import (
    BASE_CONFIG,
    CC_CONFIG,
    MI_CONFIG,
    RAW_CONFIG,
)

DIRNAME = os.path.dirname(__file__)


def func(a, b=2, c=[], d=None):
    pass


def func2(*args, **kwargs):
    pass


def func3(b=3, *args):
    pass


def fake_to_terminal():
    yield ('a', ('mystr',), {'error': True})
    yield ('b', (), {})
    yield (('p1', 'p2'), (), {'indent': 1})


def test_config_base_behavior():
    c = cli.Config(a=2, b=3)
    assert c.config_values == {'a': 2, 'b': 3}
    assert c.a == 2
    assert c.b == 3


def test_config_exceptions():
    c = cli.Config(a=2)
    assert c.__dict__, {'config_values': {'a': 2}}
    with pytest.raises(AttributeError):
        c.notexistent


def test_config_str():
    assert str(cli.Config()) == '{}'
    assert str(cli.Config(a=2)) == '{\'a\': 2}'


def test_config_eq():
    assert cli.Config() == cli.Config()
    assert cli.Config(a=2) == cli.Config(a=2)
    assert cli.Config(a=2) != cli.Config(b=2)


def test_config_for():
    assert cli.Config.from_function(func) == cli.Config(b=2, c=[], d=None)
    assert cli.Config.from_function(func2) == cli.Config()
    assert cli.Config.from_function(func3) == cli.Config(b=3)


def test_config_converts_types(mocker):
    test_config = ConfigParser()
    test_config.read_string(
        u'''
        [radon]
        str_test = B
        int_test = 19
        bool_test = true
        '''
    )
    config_mock = mocker.patch('radon.cli.FileConfig.file_config')
    config_mock.return_value = test_config

    cfg = cli.FileConfig()
    assert cfg.get_value('bool_test', bool, False) == True
    assert cfg.get_value('str_test', str, 'x') == 'B'
    assert cfg.get_value('missing_test', str, 'Y') == 'Y'
    assert cfg.get_value('int_test', int, 10) == 19


def test_cc(mocker, log_mock):
    harv_mock = mocker.patch('radon.cli.CCHarvester')
    harv_mock.return_value = mocker.sentinel.harvester

    cli.cc(['-'], json=True)

    harv_mock.assert_called_once_with(
        ['-'],
        cli.Config(
            min='A',
            max='F',
            exclude=None,
            ignore=None,
            show_complexity=False,
            average=False,
            order=getattr(cc_mod, 'SCORE'),
            no_assert=False,
            total_average=False,
            show_closures=False,
            include_ipynb=False,
            ipynb_cells=False,
        ),
    )
    log_mock.assert_called_once_with(
        mocker.sentinel.harvester,
        codeclimate=False,
        json=True,
        stream=sys.stdout,
        xml=False,
        md=False
    )


def test_raw(mocker, log_mock):
    harv_mock = mocker.patch('radon.cli.RawHarvester')
    harv_mock.return_value = mocker.sentinel.harvester

    cli.raw(['-'], summary=True, json=True)

    harv_mock.assert_called_once_with(
        ['-'],
        cli.Config(
            exclude=None,
            ignore=None,
            summary=True,
            include_ipynb=False,
            ipynb_cells=False,
        ),
    )
    log_mock.assert_called_once_with(
        mocker.sentinel.harvester, stream=sys.stdout, json=True
    )


def test_mi(mocker, log_mock):
    harv_mock = mocker.patch('radon.cli.MIHarvester')
    harv_mock.return_value = mocker.sentinel.harvester

    cli.mi(['-'], show=True, multi=False)

    harv_mock.assert_called_once_with(
        ['-'],
        cli.Config(
            min='A',
            max='C',
            exclude=None,
            ignore=None,
            show=True,
            multi=False,
            sort=False,
            include_ipynb=False,
            ipynb_cells=False,
        ),
    )
    log_mock.assert_called_once_with(
        mocker.sentinel.harvester, stream=sys.stdout, json=False
    )


def test_encoding(mocker, log_mock):
    mi_cfg = cli.Config(**BASE_CONFIG.config_values)
    mi_cfg.config_values.update(MI_CONFIG.config_values)
    raw_cfg = cli.Config(**BASE_CONFIG.config_values)
    raw_cfg.config_values.update(RAW_CONFIG.config_values)
    mappings = {
        MIHarvester: mi_cfg,
        RawHarvester: raw_cfg,
        CCHarvester: CC_CONFIG,
    }
    if sys.version_info[0] < 3:
        target = 'data/__init__.py'
    else:
        target = 'data/py3unicode.py'
    fnames = [
        os.path.join(DIRNAME, target),
        # This one will fail if detect_encoding() removes the first lines
        # See #133
        os.path.join(DIRNAME, 'data/no_encoding.py'),
    ]
    for h_class, cfg in mappings.items():
        for f in fnames:
            harvester = h_class([f], cfg)
            assert not any(
                ['error' in kw for msg, args, kw in harvester.to_terminal()]
            )


@pytest.fixture
def stdout_mock(mocker):
    return mocker.patch('radon.cli.sys.stdout.write')


def test_log(mocker, stdout_mock):
    cli.log('msg')
    cli.log('msg', indent=1)
    cli.log('{0} + 1', 2)
    cli.log('{0} + 1', 2, noformat=True)

    stdout_mock.assert_has_calls(
        [
            mocker.call('msg\n'),
            mocker.call('    msg\n'),
            mocker.call('2 + 1\n'),
            mocker.call('{0} + 1\n'),
        ]
    )
    assert stdout_mock.call_count == 4


def test_log_list(stdout_mock):
    cli.log_list([])
    cli.log_list(['msg'])

    stdout_mock.assert_called_once_with('msg\n')


def test_log_error(mocker, stdout_mock):
    reset_mock = mocker.patch('radon.cli.RESET')
    red_mock = mocker.patch('radon.cli.RED')
    bright_mock = mocker.patch('radon.cli.BRIGHT')

    bright_mock.__str__.return_value = '@'
    red_mock.__str__.return_value = '<|||>'
    reset_mock.__str__.return_value = '__R__'

    cli.log_error('mystr')

    stdout_mock.assert_called_once_with('@<|||>ERROR__R__: mystr\n')


def test_log_result(mocker, stdout_mock):
    le_mock = mocker.patch('radon.cli.log_error')
    ll_mock = mocker.patch('radon.cli.log_list')
    log_mock = mocker.patch('radon.cli.log')

    h = mocker.Mock(spec=Harvester)
    h.as_json.return_value = mocker.sentinel.json
    h.as_xml.return_value = mocker.sentinel.xml
    h.as_md.return_value = mocker.sentinel.md
    h.to_terminal.side_effect = fake_to_terminal

    cli.log_result(h, json=True)
    h.as_json.assert_called_once_with()

    h.as_json.reset_mock()
    cli.log_result(h, json=True, xml=True, md=True)
    h.as_json.assert_called_once_with()
    assert h.as_xml.call_count == 0
    assert h.as_md.call_count == 0

    cli.log_result(h, xml=True)
    h.as_xml.assert_called_once_with()

    cli.log_result(h, md=True)
    h.as_md.assert_called_once_with()

    cli.log_result(h)
    h.to_terminal.assert_called_once_with()

    log_mock.assert_has_calls(
        [
            mocker.call(mocker.sentinel.json, json=True, noformat=True),
            mocker.call(
                mocker.sentinel.json, json=True, noformat=True, xml=True, md=True
            ),
            mocker.call(mocker.sentinel.xml, noformat=True, xml=True),
            mocker.call(mocker.sentinel.md, noformat=True, md=True),
            mocker.call('a', error=True),
        ]
    )
    le_mock.assert_called_once_with('mystr', indent=1)
    ll_mock.assert_has_calls(
        [mocker.call(['b']), mocker.call(('p1', 'p2'), indent=1)]
    )
