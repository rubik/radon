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
