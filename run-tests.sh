#!/bin/bash

set -e

flake8 molo
molo scaffold testapp
flake8 testapp
pip install -e testapp
if [ ${TRAVIS_PYTHON_VERSION} == "pypy" ]; then
    coverage erase
    coverage run `which py.test` --ds=testapp.settings --verbose molo "$@"
    coverage report
else
    `which py.test` --ds=testapp.settings --verbose molo "$@"
fi
rm -rf testapp
