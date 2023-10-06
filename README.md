# Plex Scripts

A collection of scripts to enhance the Plex experience. Currently, it includes a script to calculate the remaining runtime for unwatched episodes in a selected TV series.

## Requirements

- Python 3.11+
- Plex Media Server

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
1. Ensure you have Plex Media Server running and accessible.
2. Clone this repository to your local machine.
3. Navigate to the repository directory in your terminal.
4. Install the required dependencies using the command provided above.
5. Run the script using Python 3.11 or later:
```bash
python3 show_runtime_left.py
```

## Authentication
The script uses the `keyring` library to securely store your Plex account credentials. On the first run, you will 
be prompted to enter your Plex username and password. These credentials are stored securely on your machine and 
used for subsequent runs. You can overwrite the stored token by using the `--overwrite-token` or `-O` flag when 
running the script which will force the script to ask for credentials to be stored once again.

