# Exit on any errors
$ErrorActionPreference = "Stop"

# CD to the project root
Set-Location -Path (Split-Path -Path $MyInvocation.MyCommand.Definition -Parent)

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
& .\venv\Scripts\Activate

# Install the required packages
python3 -m pip install ".[requirements, requirements_test]"
