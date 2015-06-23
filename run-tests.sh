#!/bin/bash

set -e

flake8 molo
molo scaffold testapp
pip install -e testapp
coverage erase
coverage run `which py.test` --ds=testapp.settings --verbose molo "$@"
coverage report
rm -rf testapp
