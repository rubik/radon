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
        self.assertRaises(NotImplementedError, h.gobble)

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
        sentinel = object()
        sentinel2 = object()
        cc_mock.return_value = sentinel
        fobj = mock.MagicMock()
        fobj.read.return_value = sentinel2

        h = harvest.CCHarvester([], CC_CONFIG)
        h.gobble(fobj)

        self.assertTrue(fobj.read.called)
        cc_mock.assert_called_with(sentinel2, no_assert=CC_CONFIG.no_assert)
        sr_mock.assert_called_with(sentinel, order=CC_CONFIG.order)

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
