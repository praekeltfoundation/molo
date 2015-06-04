#!/bin/bash

molo scaffold testapp
pip install -e testapp
py.test --ds=testapp.settings --verbose molo "$@"
rm -rf testapp

