# Python-AzureFakePortal

## Overview

This project provides a simple GUI tool for generating PowerShell scripts to deploy Azure Virtual Machines. The GUI is built with Tkinter and allows users to specify VM parameters, then outputs a ready-to-use `.ps1` deployment script.

## Features

- Select Azure region and VM SKU from dropdowns
- Enter resource group, VM name, network settings, and admin credentials
- Generates a PowerShell script for VM deployment
- Saves the script to your Desktop

## Usage

1. Run the Python script:

    ```sh
    python AzurePortal.py
    ```

2. Fill in all required fields in the GUI.
3. Click **Generate .ps1**.
4. The PowerShell deployment script will be saved to your Desktop.

## Requirements

- Python 3.13+
- Tkinter (usually included with Python)

## File Structure

- [`AzurePortal.py`](AzurePortal.py): Main GUI application
- `README.md`: Project documentation

## License

MIT License