#!/bin/bash
rm -r build/
rm -r dist/
python setup.py sdist bdist_wheel
twine upload dist/*
