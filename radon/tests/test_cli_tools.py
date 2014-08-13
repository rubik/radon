import os
import sys
import unittest
import radon.cli.tools as tools
try:
    import unittest.mock as mock
except ImportError:
    import mock


def fake_isfile(filename):
    if filename == 'file.py':
        return True
    return False


def fake_walk():
    yield '.', ['tests', 'sub', '.hid'], ['tox.ini', 'amod.py', 'test_all.py']
    yield './tests', [], ['test_amod.py', 'run.py', '.hid.py']
    yield './sub', [], ['amod.py', 'bmod.py']


class TestTools(unittest.TestCase):

    def test_open(self):
        with tools._open('-') as fobj:
            self.assertTrue(fobj is sys.stdin)

        m = mock.mock_open()
        with mock.patch('radon.cli.tools.open', m, create=True):
            tools._open('randomfile.py').__enter__()
        m.assert_called_with('randomfile.py')

    @mock.patch('radon.cli.tools.os.path')
    @mock.patch('radon.cli.tools.os')
    def test_iter_filenames(self, os_mod, os_path_mod):
        iter_files = lambda *a, **kw: list(tools.iter_filenames(*a, **kw))

        self.assertEqual(iter_files(['-']), ['-'])

        os_path_mod.normpath = os.path.normpath
        os_path_mod.basename = os.path.basename
        os_path_mod.join = os.path.join
        os_path_mod.isfile.side_effect = fake_isfile
        os_mod.walk.return_value = fake_walk()

        self.assertEqual(iter_files(['file.py', 'random/path']),
                         ['file.py', 'amod.py', 'test_all.py',
                          'tests/test_amod.py', 'tests/run.py', 'sub/amod.py',
                          'sub/bmod.py'])
