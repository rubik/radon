#!/bin/python

import os
import sys
import subprocess

deps = []
pyv = os.environ.get('TRAVIS_PYTHON_VERSION', '%s.%s' % sys.version_info[:2])
if pyv == '2.6':
    deps.extend(['unittest2', 'argparse', 'importlib', 'mock'])
elif pyv in ('2.7', '3.2', 'pypy'):
    deps.append('mock')

if deps:
    subprocess.call(['pip', 'install'] + deps)
