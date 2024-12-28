#!/bin/bash

echo 'clean up any previous demo...'
rm -r ~/.local/paper
# Assumes `build` is available in the current environment.
# Installing with Pipx works well.
echo 'build project wheel...'
pyproject-build > /dev/null
echo 'make zipapp...'
./make-zipapp
echo 'deploy from zipapp...'
dist/install-paper-0.1.0-for-py3.pyz
