#!/bin/bash

cp -a $REPO ./build/$NAME

${PIP} install -r $REPO/mobi-application/requirements.txt

