#!/bin/bash

rm -rf build/ && \
rm -rf dist/ && \
rm -rf ytmgrab.egg-info/ && \
rm -rf ytmgrab/__pycache__ && \
rm -rf ytmgrab/backend/__pycache__ && \
rm ytmgrab-*.pkg.tar.zst
