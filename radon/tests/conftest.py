import pytest
import textwrap
import os


class RadonConfig(object):
    def __init__(self):
        self._fname = os.path.join(os.path.dirname(__file__), 'radon.cfg')

    def write(self, text):
        _cfg = textwrap.dedent(text)
        with open(self._fname, 'w') as cfg_f:
            cfg_f.write("# Autogenerated from pytest \n[radon]\n")
            cfg_f.write(_cfg)

    def __del__(self):
        with open(self._fname, 'w') as cfg_f:
            cfg_f.write('# Session completed')


@pytest.fixture(scope="session")
def radon_config():
    r = RadonConfig()
    yield r
    del r
