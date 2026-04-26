#!/bin/bash

# Build script for Render backend deployment
set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Backend build complete!"
