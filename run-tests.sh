#!/bin/bash

set -e

flake8 molo
molo scaffold testapp
pip install -e testapp
py.test --ds=testapp.settings --verbose molo "$@"
rm -rf testapp
