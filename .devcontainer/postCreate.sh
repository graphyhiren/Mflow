#!/bin/bash

# Turn off git status check to speed up zsh prompt: https://stackoverflow.com/a/25864063
git config --add oh-my-zsh.hide-status 1
git config --add oh-my-zsh.hide-dirty 1
pip install --no-deps -e .
