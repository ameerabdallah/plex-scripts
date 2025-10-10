# Plex Scripts

A collection of Python scripts to enhance your Plex Media Server experience. Features include calculating remaining runtime for unwatched content and managing recently added items.

## Requirements

- Python 3.11+
- Plex Media Server with accessible API
- Plex account credentials

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

All scripts are run through the unified `plex_scripts.py` entry point:

```bash
python plex_scripts.py <command> [options]
```

### Global Options

- `-o, --overwrite-token` - Force reauthentication with Plex (applies to all commands)

## Available Commands

### Runtime Calculator

Calculate the remaining runtime for unwatched episodes in TV series or entire libraries. The script automatically excludes intros and credits for accurate time estimates.

**Command:** `show-runtime-left` (aliases: `srtl`, `runtime-left`, `rtl`)

**Features:**
- Calculate runtime for individual shows or entire libraries
- Automatically detects and excludes intro/credit markers
- Parallel processing for faster marker retrieval
- Interactive fuzzy search for selecting content

**Options:**
- `-e, --entire-library` - Calculate runtime for all items in the selected library
- `-s, --skip-markers` - Skip marker calculation (faster, but includes intros/credits in total)

**Examples:**

```bash
# Calculate for a single show (interactive selection)
python plex_scripts.py show-runtime-left

# Calculate for entire library
python plex_scripts.py show-runtime-left --entire-library

# Skip marker calculation (faster, but less accurate)
python plex_scripts.py show-runtime-left --skip-markers

# Force reauthentication
python plex_scripts.py --overwrite-token show-runtime-left
```

**Note:** Marker calculation requires fetching data for each episode individually. This is parallelized for performance but can still be slow for large libraries. Use `--skip-markers` for faster results if precise runtime isn't critical.

### Push to Recently Added

Update the "added date" of media items to push them to the top of your "Recently Added" section in Plex.

**Command:** `push-recently-added`

**Features:**
- Works with movies, shows, seasons, or individual episodes
- Recursively updates all child items (e.g., updating a show updates all seasons/episodes)
- Interactive selection with fuzzy search

**Arguments:**
- `movie` - Push a movie to recently added
- `show` - Push an entire show to recently added
- `season` - Push a season to recently added
- `episode` - Push a single episode to recently added

**Examples:**

```bash
# Push a movie
python plex_scripts.py push-recently-added movie

# Push an entire show (updates all seasons and episodes)
python plex_scripts.py push-recently-added show

# Push a specific season
python plex_scripts.py push-recently-added season

# Push a single episode
python plex_scripts.py push-recently-added episode
```

## Authentication

All scripts use the `keyring` library to securely store your Plex authentication token on your local machine.

**First Run:**
1. You'll be prompted for your Plex username and password
2. After successful authentication, your token is stored securely
3. Subsequent runs use the stored token automatically

**Reauthentication:**
If your token expires or becomes invalid, use the `--overwrite-token` or `-o` flag to force reauthentication.

**Security:**
- Credentials are stored using your system's secure credential storage (Keychain on macOS, Credential Manager on Windows, Secret Service on Linux)
- Passwords are never stored; only authentication tokens are retained

## Development

### Library Files

The codebase includes reusable library modules:

- `authenticate_plex.py` - Handles Plex authentication and token management
- `get_plex_objects.py` - Provides interactive selection functions for servers, libraries, shows, etc.

These can be imported when creating new scripts.

### Adding New Scripts

To add a new script to the unified interface:

1. Create your script file (e.g., `my_script.py`)
2. Implement `add_arguments(subparser)` to register CLI arguments
3. Implement `run(account, **kwargs)` as the main entry point
4. Return a script name constant for routing
5. Import and register in `plex_scripts.py`

