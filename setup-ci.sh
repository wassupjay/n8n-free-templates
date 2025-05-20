#!/bin/bash
# Setup script for n8n workflow validation and visualization

set -e

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Create and activate a virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LIB_DIR="${SCRIPT_DIR}/lib"

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip

# Change to lib directory and install the package
pushd "$LIB_DIR" > /dev/null
pip install -r requirements.txt
pip install -e .
popd > /dev/null

echo ""
echo "✅ Setup complete!"
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To validate all n8n workflows, run:"
echo "  cd lib && n8n-validate .. && cd .."
echo ""
echo "To visualize a workflow, run:"
echo "  cd lib && n8n-visualize ../path/to/workflow.json && cd .."

# Run validation if this is a CI environment
if [ "$CI" = "true" ]; then
    echo "Running in CI environment. Validating workflows..."
    pushd "$LIB_DIR" > /dev/null
    if ! n8n-validate ..; then
        echo "❌ Workflow validation failed"
        exit 1
    fi
    echo "✅ All workflows are valid!"
    popd > /dev/null
fi
