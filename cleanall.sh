#!/bin/bash

rm -rf smytm/__pycache__/
rm -rf .pybuild/
rm -rf dist/

rm -rf build/
rm -rf pkg/
rm -rf src/
rm -f smytm-*.pkg.tar.zst

rm -rf debian/.debhelper/
rm -rf debian/smytm/
rm -f debian/debhelper-build-stamp
rm -f debian/files
rm -f debian/*.substvars
rm -f debian/*.debhelper
rm -f debian/*.log
rm -f smytm_*.deb
rm -f ../smytm_*.deb
rm -f ../smytm_*.buildinfo
rm -f ../smytm_*.changes

rm -rf rpm/BUILD/*
rm -rf rpm/BUILDROOT/*
rm -rf rpm/RPMS/*
rm -rf rpm/SOURCES/*
rm -rf rpm/SRPMS/*
rm -f smytm-*.rpm
