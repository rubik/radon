import unittest
import radon.cli as cli
import radon.complexity as cc_mod
from radon.cli.harvest import Harvester
try:
    import unittest.mock as mock
except ImportError:
    import mock


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


class TestConfig(unittest.TestCase):

    def test_base_behavior(self):
        c = cli.Config(a=2, b=3)
        self.assertEqual(c.config_values, {'a': 2, 'b': 3})
        self.assertEqual(c.a, 2)
        self.assertEqual(c.b, 3)

    def test_exceptions(self):
        c = cli.Config(a=2)
        self.assertEqual(c.__dict__, {'config_values': {'a': 2}})
        self.assertRaises(AttributeError, lambda: c.notexistent)

    def test_str(self):
        self.assertEqual(str(cli.Config()), '{}')
        self.assertEqual(str(cli.Config(a=2)), '{\'a\': 2}')

    def test_eq(self):
        self.assertEqual(cli.Config(), cli.Config())
        self.assertEqual(cli.Config(a=2), cli.Config(a=2))
        self.assertNotEqual(cli.Config(a=2), cli.Config(b=2))

    def test_for(self):
        self.assertEqual(cli.Config.from_function(func),
                         cli.Config(b=2, c=[], d=None))
        self.assertEqual(cli.Config.from_function(func2), cli.Config())
        self.assertEqual(cli.Config.from_function(func3), cli.Config(b=3))


class TestCommands(unittest.TestCase):

    @mock.patch('radon.cli.log_result')
    @mock.patch('radon.cli.CCHarvester')
    def test_cc(self, harv_mock, log_mock):
        harv_mock.return_value = mock.sentinel.harvester

        cli.cc(['-'], json=True)

        harv_mock.assert_called_once_with(['-'], cli.Config(
            min='A', max='F', exclude=None, ignore=None, show_complexity=False,
            average=False, order=getattr(cc_mod, 'SCORE'), no_assert=False,
            total_average=False, show_closures=False))
        log_mock.assert_called_once_with(mock.sentinel.harvester, codeclimate=False, json=True,
                                         xml=False)

    @mock.patch('radon.cli.log_result')
    @mock.patch('radon.cli.RawHarvester')
    def test_raw(self, harv_mock, log_mock):
        harv_mock.return_value = mock.sentinel.harvester

        cli.raw(['-'], summary=True, json=True)

        harv_mock.assert_called_once_with(['-'], cli.Config(exclude=None,
                                                            ignore=None,
                                                            summary=True))
        log_mock.assert_called_once_with(mock.sentinel.harvester, json=True)

    @mock.patch('radon.cli.log_result')
    @mock.patch('radon.cli.MIHarvester')
    def test_mi(self, harv_mock, log_mock):
        harv_mock.return_value = mock.sentinel.harvester

        cli.mi(['-'], show=True, multi=False)

        harv_mock.assert_called_once_with(['-'], cli.Config(
            min='A', max='C', exclude=None, ignore=None, show=True,
            multi=False))
        log_mock.assert_called_once_with(mock.sentinel.harvester, json=False)


@mock.patch('radon.cli.sys.stdout.write')
class TestLogging(unittest.TestCase):

    def test_log(self, stdout_mock):
        cli.log('msg')
        cli.log('msg', indent=1)
        cli.log('{0} + 1', 2)
        cli.log('{0} + 1', 2, noformat=True)

        stdout_mock.assert_has_calls([
            mock.call('msg\n'),
            mock.call('    msg\n'),
            mock.call('2 + 1\n'),
            mock.call('{0} + 1\n'),
        ])
        self.assertEqual(stdout_mock.call_count, 4)

    def test_log_list(self, stdout_mock):
        cli.log_list([])
        cli.log_list(['msg'])

        stdout_mock.assert_called_once_with('msg\n')

    @mock.patch('radon.cli.RESET')
    @mock.patch('radon.cli.RED')
    @mock.patch('radon.cli.BRIGHT')
    def test_log_error(self, bright_mock, red_mock, reset_mock, stdout_mock):
        bright_mock.__str__.return_value = '@'
        red_mock.__str__.return_value = '<|||>'
        reset_mock.__str__.return_value = '__R__'

        cli.log_error('mystr')

        stdout_mock.assert_called_once_with('@<|||>ERROR__R__: mystr\n')

    @mock.patch('radon.cli.log_error')
    @mock.patch('radon.cli.log_list')
    @mock.patch('radon.cli.log')
    def test_log_result(self, log_mock, ll_mock, le_mock, stdout_mock):
        h = mock.Mock(spec=Harvester)
        h.as_json.return_value = mock.sentinel.json
        h.as_xml.return_value = mock.sentinel.xml
        h.to_terminal.side_effect = fake_to_terminal

        cli.log_result(h, json=True)
        h.as_json.assert_called_once_with()

        h.as_json.reset_mock()
        cli.log_result(h, json=True, xml=True)
        h.as_json.assert_called_once_with()
        self.assertEqual(h.as_xml.call_count, 0)

        cli.log_result(h, xml=True)
        h.as_xml.assert_called_once_with()

        cli.log_result(h)
        h.to_terminal.assert_called_once_with()

        log_mock.assert_has_calls([
            mock.call(mock.sentinel.json, noformat=True),
            mock.call(mock.sentinel.json, noformat=True),
            mock.call(mock.sentinel.xml, noformat=True),
            mock.call('a'),
        ])
        le_mock.assert_called_once_with('mystr', indent=1)
        ll_mock.assert_has_calls([
            mock.call(['b']),
            mock.call(('p1', 'p2'), indent=1),
        ])
