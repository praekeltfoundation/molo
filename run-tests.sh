#!/bin/bash

set -e

flake8 molo
molo scaffold testapp
flake8 testapp
pip install -e testapp
if [ ${TRAVIS_PYTHON_VERSION} == "pypy" ]; then
    `which py.test` --ds=testapp.settings --verbose molo "$@"
else
    coverage erase
    coverage run `which py.test` --ds=testapp.settings --verbose molo "$@"
    coverage report
fi
rm -rf testapp
