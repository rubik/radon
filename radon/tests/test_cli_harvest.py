import unittest
import collections
from radon.cli import Config
import radon.cli.harvest as harvest
try:
    import unittest.mock as mock
except ImportError:
    import mock

BASE_CONFIG = Config(
    exclude='test_[^.]+\.py',
    ignore='tests,docs',
)

CC_CONFIG = Config(
    order='SCORE',
    no_assert=False,
    min='B',
    max='F',
    show_complexity=False,
    average=True,
    total_average=False,
    **BASE_CONFIG.config_values
)

RAW_CONFIG = Config(
    summary=True,
)

MI_CONFIG = Config(
    multi=True,
    min='B',
    max='C',
    show=True,
)


def fake_gobble(fobj):
    return 42


def fake_gobble_raising(fobj):
    raise TypeError('mystr')


def fake_run():
    for i in range(3):
        yield {'file-{0}'.format(i): i**2}


class TestBaseHarvester(unittest.TestCase):

    @mock.patch('radon.cli.harvest.iter_filenames')
    def test_iter_filenames(self, iter_mock):
        h = harvest.Harvester([], BASE_CONFIG)
        h._iter_filenames()

        iter_mock.assert_called_with([], BASE_CONFIG.exclude,
                                     BASE_CONFIG.ignore)

    def test_gobble_not_implemented(self):
        h = harvest.Harvester([], BASE_CONFIG)
        self.assertRaises(NotImplementedError, h.gobble, None)

    def test_as_xml_not_implemented(self):
        h = harvest.Harvester([], BASE_CONFIG)
        self.assertRaises(NotImplementedError, h.as_xml)

    def test_to_terminal_not_implemented(self):
        h = harvest.Harvester([], BASE_CONFIG)
        self.assertRaises(NotImplementedError, h.to_terminal)

    def test_run(self):
        h = harvest.Harvester(['-'], BASE_CONFIG)
        h.gobble = fake_gobble
        self.assertTrue(isinstance(h.run(), collections.Iterator))
        self.assertEqual(list(h.run()), [('-', 42)])
        h.gobble = fake_gobble_raising
        self.assertEqual(list(h.run()), [('-', {'error': 'mystr'})])

    def test_results(self):
        h = harvest.Harvester([], BASE_CONFIG)
        h.run = fake_run
        results = h.results
        self.assertTrue(isinstance(results, collections.Iterator))
        self.assertEqual(list(results), [{'file-0': 0}, {'file-1': 1},
                                         {'file-2': 4}])
        self.assertFalse(isinstance(h.results, collections.Iterator))
        self.assertTrue(isinstance(h.results, collections.Iterable))
        self.assertTrue(isinstance(h.results, list))

    def test_as_json(self):
        h = harvest.Harvester([], BASE_CONFIG)
        h._results = {'filename': {'complexity': 2}}
        self.assertEqual(h.as_json(), '{"filename": {"complexity": 2}}')


class TestCCHarvester(unittest.TestCase):

    @mock.patch('radon.cli.harvest.sorted_results')
    @mock.patch('radon.cli.harvest.cc_visit')
    def test_gobble(self, cc_mock, sr_mock):
        cc_mock.return_value = mock.sentinel.one
        fobj = mock.MagicMock()
        fobj.read.return_value = mock.sentinel.two

        h = harvest.CCHarvester([], CC_CONFIG)
        h.gobble(fobj)

        self.assertTrue(fobj.read.called)
        cc_mock.assert_called_with(mock.sentinel.two,
                                   no_assert=CC_CONFIG.no_assert)
        sr_mock.assert_called_with(mock.sentinel.one, order=CC_CONFIG.order)

    @mock.patch('radon.cli.harvest.cc_to_dict')
    def test_to_dicts(self, c2d_mock):
        c2d_mock.side_effect = lambda i: i
        h = harvest.CCHarvester([], CC_CONFIG)
        sample_results = [('a', [{'rank': 'A'}]), ('b', [{'rank': 'B'}])]
        h._results = sample_results

        self.assertEqual(h._to_dicts(), dict(sample_results))
        self.assertEqual(c2d_mock.call_count, 2)

    @mock.patch('radon.cli.harvest.dict_to_xml')
    def test_as_json_xml(self, d2x_mock):
        to_dicts_mock = mock.MagicMock()
        to_dicts_mock.return_value = {'a': {'rank': 'A'}}

        h = harvest.CCHarvester([], CC_CONFIG)
        h._to_dicts = to_dicts_mock
        self.assertEqual(h.as_json(), '{"a": {"rank": "A"}}')

        h.as_xml()
        self.assertTrue(d2x_mock.called)
        d2x_mock.assert_called_with(to_dicts_mock.return_value)
        self.assertEqual(to_dicts_mock.call_count, 2)

    @mock.patch('radon.cli.harvest.RESET')
    @mock.patch('radon.cli.harvest.RANKS_COLORS')
    @mock.patch('radon.cli.harvest.cc_to_terminal')
    def test_to_terminal(self, c2t_mock, ranks_mock, reset_mock):
        h = harvest.CCHarvester([], CC_CONFIG)
        h._results = [
            ('a', {'error': 'mystr'}), ('b', {})
        ]
        c2t_mock.return_value = (['res'], 9, 3)
        ranks_mock.__getitem__.return_value = '<|A|>'
        reset_mock.__eq__.side_effect = lambda o: o == '__R__'

        results = list(h.to_terminal())
        c2t_mock.assert_called_once_with({}, CC_CONFIG.show_complexity,
                                         CC_CONFIG.min, CC_CONFIG.max,
                                         CC_CONFIG.total_average)
        self.assertEqual(results, [
            ('a', ('mystr',), {'error': True}),
            ('b', (), {}),
            (['res'], (), {'indent': 1}),
            ('\n{0} blocks (classes, functions, methods) analyzed.', (3,), {}),
            ('Average complexity: {0}{1} ({2}){3}',
             ('<|A|>', 'A', 3, '__R__'), {}),
        ])


class TestRawHarvester(unittest.TestCase):

    @mock.patch('radon.cli.harvest.raw_to_dict')
    @mock.patch('radon.cli.harvest.analyze')
    def test_gobble(self, analyze_mock, r2d_mock):
        fobj = mock.MagicMock()
        fobj.read.return_value = mock.sentinel.one
        analyze_mock.return_value = mock.sentinel.two

        h = harvest.RawHarvester([], RAW_CONFIG)
        h.gobble(fobj)

        self.assertEqual(fobj.read.call_count, 1)
        analyze_mock.assert_called_once_with(mock.sentinel.one)
        r2d_mock.assert_called_once_with(mock.sentinel.two)

    def test_as_xml(self):
        h = harvest.RawHarvester([], RAW_CONFIG)
        self.assertRaises(NotImplementedError, h.as_xml)

    def test_to_terminal(self):
        h = harvest.RawHarvester([], RAW_CONFIG)
        h._results = [
            ('a', {'error': 'mystr'}),
            ('b', {'loc': 24, 'lloc': 27, 'sloc': 15, 'comments': 3,
                   'multi': 3, 'blank': 9}),
            ('c', {'loc': 24, 'lloc': 27, 'sloc': 15, 'comments': 3,
                   'multi': 3, 'blank': 9}),
        ]

        self.assertEqual(list(h.to_terminal()), [
            ('a', ('mystr',), {'error': True}),
            ('b', (), {}),
            ('{0}: {1}', ('LOC', 24), {'indent': 1}),
            ('{0}: {1}', ('LLOC', 27), {'indent': 1}),
            ('{0}: {1}', ('SLOC', 15), {'indent': 1}),
            ('{0}: {1}', ('Comments', 3), {'indent': 1}),
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
            ('{0}: {1}', ('Multi', 3), {'indent': 1}),
            ('{0}: {1}', ('Blank', 9), {'indent': 1}),
            ('- Comment Stats', (), {'indent': 1}),
            ('(C % L): {0:.0%}', (0.125,), {'indent': 2}),
            ('(C % S): {0:.0%}', (0.2,), {'indent': 2}),
            ('(C + M % L): {0:.0%}', (0.25,), {'indent': 2}),
            ('** Total **', (), {}),
            ('{0}: {1}', ('LOC', 48), {'indent': 1}),
            ('{0}: {1}', ('LLOC', 54), {'indent': 1}),
            ('{0}: {1}', ('SLOC', 30), {'indent': 1}),
            ('{0}: {1}', ('Comments', 6), {'indent': 1}),
            ('{0}: {1}', ('Multi', 6), {'indent': 1}),
            ('{0}: {1}', ('Blank', 18), {'indent': 1}),
        ])


class TestMIHarvester(unittest.TestCase):

    @mock.patch('radon.cli.harvest.mi_visit')
    def test_gobble(self, mv_mock):
        fobj = mock.MagicMock()
        fobj.read.return_value = mock.sentinel.one
        mv_mock.return_value = mock.sentinel.two

        h = harvest.MIHarvester([], MI_CONFIG)
        result = h.gobble(fobj)

        self.assertEqual(fobj.read.call_count, 1)
        mv_mock.assert_called_once_with(mock.sentinel.one, MI_CONFIG.multi)
        self.assertEqual(result, {'mi': mock.sentinel.two})

    def test_as_xml(self):
        h = harvest.MIHarvester([], MI_CONFIG)
        self.assertRaises(NotImplementedError, h.as_xml)

    @mock.patch('radon.cli.harvest.RESET')
    @mock.patch('radon.cli.harvest.MI_RANKS')
    def test_to_terminal(self, ranks_mock, reset_mock):
        ranks_mock.__getitem__.side_effect = lambda j: '<|{0}|>'.format(j)
        reset_mock.__eq__.side_effect = lambda o: o == '__R__'

        h = harvest.MIHarvester([], MI_CONFIG)
        h._results = [
            ('a', {'error': 'mystr'}),
            ('b', {'mi': 25}),
            ('c', {'mi': 15}),
            ('d', {'mi': 0}),
        ]

        self.assertEqual(list(h.to_terminal()), [
            ('a', ('mystr',), {'error': True}),
            ('{0} - {1}{2}{3}{4}', ('c', '<|B|>', 'B', ' (15.00)', '__R__'),
             {}),
            ('{0} - {1}{2}{3}{4}', ('d', '<|C|>', 'C', ' (0.00)', '__R__'),
             {}),
        ])
