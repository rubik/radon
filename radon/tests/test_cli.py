import os.path
from radon.cli import cc, mi, raw
from paramunittest import *


RADON_DIR = os.path.dirname(os.path.dirname(__file__))


@parametrized((cc,), (mi,), (raw,))
class TestGeneralCommands(ParametrizedTestCase):

    def setParameters(self, command):
        self.command = command

    def testItWorks(self):
        self.assertTrue(self.command(RADON_DIR) is None)
