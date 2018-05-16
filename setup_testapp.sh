#!/usr/bin/env bash

set -e # Exit whenever a command fails
set -x # Output commands run to see them in the Travis interface

molo scaffold testapp
mkdir -p testapp/testapp/templates/registration/
cp molo/profiles/test_templates/login.html testapp/testapp/templates/registration/
cp local_test_settings.py testapp/testapp/settings/local.py
