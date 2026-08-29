#!/bin/bash

rm -rf smytm/__pycache__/
rm -rf smytm/*.pyc
rm -rf .pytest_cache/
rm -rf .pybuild/
rm -rf dist/
rm -rf build/
rm -rf pkg/
rm -rf src/
rm -rf rpm/BUILD/*
rm -rf rpm/BUILDROOT/*
rm -rf rpm/RPMS/*
rm -rf rpm/SOURCES/*
rm -rf rpm/SRPMS/*
rm -f smytm-*.pkg.tar.zst
rm -f smytm-*.rpm
rm -f *.egg-info/
