import os.path
import tempfile
import shutil
from radon.cli import cc, mi, raw
from radon.tools import iter_filenames
from paramunittest import *


RADON_DIR = os.path.dirname(os.path.dirname(__file__))


@parametrized((cc,), (mi,), (raw,))
class TestGeneralCommands(ParametrizedTestCase):

    def setParameters(self, command):
        self.command = command

    def testItWorks(self):
        self.assertTrue(self.command(RADON_DIR) is None)

    def testIterFilenames(self):
        tmpdir = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(tmpdir, 'd1'))
            f1 = os.path.join(tmpdir, 'd1', 't1.py')
            open(f1, 'w').close()
            f2 = os.path.join(tmpdir, 'd1', 't2.py')
            open(f2, 'w').close()
            os.makedirs(os.path.join(tmpdir, 'd2'))
            f3 = os.path.join(tmpdir, 'd2', 't3.py')
            open(f3, 'w').close()
            f4 = os.path.join(tmpdir, 'd2', 't4.py')
            open(f4, 'w').close()

            dir1 = [os.path.join(tmpdir, 'd1')]
            dir12 = [os.path.join(tmpdir, 'd1'), os.path.join(tmpdir, 'd2')]
            dirall = [tmpdir]

            # Test without excludes
            exclude = ''
            names = iter_filenames(dirall, exclude)
            self.assertEqual(set(names), set([f1, f2, f3, f4]))
            names = iter_filenames(dir12, exclude)
            self.assertEqual(set(names), set([f1, f2, f3, f4]))
            names = iter_filenames(dir1, exclude)
            self.assertEqual(set(names), set([f1, f2]))

            # Test with one exclude
            exclude = '*/t2.py'
            names = iter_filenames(dirall, exclude)
            self.assertEqual(set(names), set([f1, f3, f4]))
            names = iter_filenames(dir12, exclude)
            self.assertEqual(set(names), set([f1, f3, f4]))
            names = iter_filenames(dir1, exclude)
            self.assertEqual(set(names), set([f1]))

            # Test with two excludes
            exclude = '*/t2.py,*/d2/*'
            names = iter_filenames(dirall, exclude)
            self.assertEqual(set(names), set([f1]))
            names = iter_filenames(dir12, exclude)
            self.assertEqual(set(names), set([f1]))
            names = iter_filenames(dir1, exclude)
            self.assertEqual(set(names), set([f1]))
        finally:
            shutil.rmtree(tmpdir)

