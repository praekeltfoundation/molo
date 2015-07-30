#!/bin/bash

set -e

flake8 molo
molo scaffold testapp
flake8 testapp
pip install -e testapp
`which py.test` --ds=testapp.settings --verbose molo "$@"
rm -rf testapp
