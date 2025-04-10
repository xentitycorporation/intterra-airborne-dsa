# airborne-dsa-lite

Data shipping script for airborne products

## Local Development

### Prerequisites

- Python 3 installed
- Python 3 venv installed
- `python -m venv env`
- `source env/bin/activate` or `.\env\Scripts\Activate.ps1` For PowerShell
- `python -m pip install --upgrade pip setuptools pyinstaller`

### Running locally

## Getting started

- Rename sample.config to config.json
- Edit config.json with provided information from your agency
- `source env/bin/activate`
- `python -m pip install -e .` or `.\env\Scripts\Activate.ps1` For PowerShell
- `python main.py`

For running locally, add "storageMode": "local" to config.json

## Generating build
- `pyinstaller main.py --onefile --version-file=build_version.txt -n egp-airborne-dsa`

### Adding an Icon to the Executable (Optional)

To add an icon to the generated executable:

1. Prepare an `.ico` file for your application.
2. Add the `--icon=<path_to_icon_file>` option to the `pyinstaller` command:
    ```bash
    pyinstaller main.py --onefile --version-file=build_version.txt --icon=<path_to_icon_file> -n egp-airborne-dsa
    ```
    Replace `<path_to_icon_file>` with the path to your `.ico` file.

## Running unit tests

- `python -m unittest`
