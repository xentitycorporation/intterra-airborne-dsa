# airborne-dsa-lite

Data shipping script for airborne products

## Local Development

### Prerequisites

- Python 3 installed
- Python 3 venv installed
- `python3 -m venv env`
- `source env/bin/activate`
- `python3 -m pip install --upgrade pip setuptools pyinstaller`

### Running locally

## Getting started

- `source env/bin/activate`
- `python3 -m pip install -e .`
- `python3 main.py`

For running locally, add "storageMode": "local" to config.json

## Generating build

- `pyinstaller main.py --onefile -n airborne-dsa`

## Running unit tests

- `python3 -m unittest`

