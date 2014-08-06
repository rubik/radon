#!/bin/bash
set -ev

if [[ "${TRAVIS_PYTHON_VERSION}" == "2.6" ]]; then
    pip install unittest2 argparse importlib
fi
