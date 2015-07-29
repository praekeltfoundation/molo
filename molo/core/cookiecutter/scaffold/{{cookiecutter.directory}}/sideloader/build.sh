#!/bin/bash

cp -a $REPO ./build/$NAME

${PIP} install -r $REPO/{{cookiecutter.app_name}}/requirements.txt

