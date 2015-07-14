#!/bin/python

import os
import sys
import subprocess

deps = []
undeps = []
pyv = os.environ.get('TRAVIS_PYTHON_VERSION', '%s.%s' % sys.version_info[:2])
if pyv == '2.6':
    deps.extend(['unittest2', 'argparse', 'importlib', 'mock'])
elif pyv == '3.2':
    undeps.append('coverage')
    deps.append('coverage==3.7.1')

if undeps:
    subprocess.call(['pip', 'uninstall', '-y'] + undeps)
if deps:
    subprocess.call(['pip', 'install'] + deps)
