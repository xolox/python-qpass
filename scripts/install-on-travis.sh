#!/bin/bash -e

# Install the required Python packages.
pip install --requirement=requirements-travis.txt

# Install the project itself, making sure that potential character encoding
# and/or decoding errors in the setup script are caught as soon as possible.
LC_ALL=C pip install .
