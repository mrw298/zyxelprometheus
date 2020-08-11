#!/bin/bash

coverage run test.py

let R=$?

coverage report --omit="*/site-packages/*","test.py","tests/*"

coverage html --omit="*/site-packages/*","test.py","tests/*"

exit $R
