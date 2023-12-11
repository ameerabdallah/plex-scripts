# Plex Scripts

A collection of scripts to enhance the Plex experience. Currently, it includes a script to calculate the remaining runtime for unwatched episodes in a selected TV series.

## Requirements

- Python 3.11+

## Installation

Install the required dependencies using the following command:

```bash
pip install -r requirements.txt
```

## Script: `show_runtime_left.py`
This script calculates the remaining runtime for unwatched episodes in a selected TV series on your Plex server. 
It prompts the user to select a server, a library, and a TV series, then computes the total remaining runtime, 
excluding intros and credits.

### Usage
* Normal usage:
```bash
python show_runtime_left.py
```

* Overwrite stored Plex authentication token
```bash
python show_runtime_left.py --overwrite-token 
# or 
python show_runtime_left.py -o
```

* Calculate for entire library
```bash
python show_runtime_left.py --entire-library
# or
python show_runtime_left.py -e
```

* Skip marker calculation. This is useful since markers need to be pulled for each episode of a series 1 by 1. This is parallelized to improve performance but is still orders of magnitude slower than simply skipping the marker calculation.
```bash
python show_runtime_left.py --skip-markers
# or
python show_runtime_left.py -s
```

## Authentication
The scripts in this repo that require authentication use the `keyring` library to securely store your Plex account credentials. 
On the first run, you will be prompted to enter your Plex username and password.  After verifying credentials with Plex's servers,
the token that is received from Plex is stored securely on your machine and used for subsequent runs. If you want to have a nice wrapper
for authentication while keeping the stored credential, you can use the `authenticate_plex.py` library file to handle authentication for you.

