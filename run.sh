#!/bin/bash

# Stop if any command fails
set -e

echo "Starting Trip Planner application..."

# ---------------------------------
# 1. Create virtual environment
# ---------------------------------

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# ---------------------------------
# 2. Activate virtual environment
# ---------------------------------

source venv/bin/activate

# ---------------------------------
# 3. Upgrade pip
# ---------------------------------

echo "Updating pip..."
python -m pip install --upgrade pip

# ---------------------------------
# 4. Install dependencies
# ---------------------------------

echo "Installing dependencies..."
pip install -r requirements.txt

# ---------------------------------
# 5. Create required directories
# ---------------------------------

mkdir -p logs
mkdir -p instance

# ---------------------------------
# 6. Run tests
# ---------------------------------

echo "Running tests..."
pytest test.py -v

# ---------------------------------
# 7. Start Flask application
# ---------------------------------

echo "Starting Flask server..."

python run.py