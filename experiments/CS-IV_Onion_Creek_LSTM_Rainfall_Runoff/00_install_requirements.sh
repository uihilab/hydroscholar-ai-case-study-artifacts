#!/usr/bin/env sh
set -e

echo "Starting installation of Python requirements..."

# Ensure pip is up to date using python3 -m pip for portability
echo "Upgrading pip..."
python3 -m pip install --upgrade pip

# List of required packages
REQUIREMENTS="numpy pandas requests tensorflow scikit-learn hydrostats"

# Install each package
for PACKAGE in $REQUIREMENTS; do
  echo "Installing ${PACKAGE}..."
  python3 -m pip install "${PACKAGE}"
done

echo "All Python requirements have been installed successfully."