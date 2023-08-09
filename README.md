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
-

## Generating build

- `pyinstaller main.py`

- Make sure you have python 3 installed

- `pip install awscli boto3`
- `aws configure`
- Set the correct bucket name in `settings.py`

Run: `python main.py` or `intterra-airborne-dsa.bat`

Drop KMLs or tifs (*.tif and*.tiff) into this directory
