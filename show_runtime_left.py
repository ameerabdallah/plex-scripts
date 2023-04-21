#!/usr/bin/env python

import argparse
from typing import cast, List
from plexapi.media import Marker
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.library import LibrarySection, ShowSection 
from plexapi.video import Show, Episode
import keyring
import getpass
from iterfzf import iterfzf
from tqdm import tqdm
import datetime


PLEX_SERVICE_NAME = "plex_api"
PLEX_SERVICE_NAME_USERNAME = "plex_api_username"

def handle_plex_authentication(overwrite_token: bool) -> MyPlexAccount:
    credentials = None
    username = None
    if overwrite_token == False:
        username = keyring.get_password(PLEX_SERVICE_NAME, PLEX_SERVICE_NAME_USERNAME)
        credentials = keyring.get_credential(PLEX_SERVICE_NAME, username)

    if credentials is not None:
        token = cast(str, credentials.password)
        return MyPlexAccount(username=username, token=token)
    else:
        username = input("Username: ")
        password = getpass.getpass(f'Password for {username}: ')
        account = MyPlexAccount(username, password)
        token = account.authenticationToken
        keyring.set_password(PLEX_SERVICE_NAME, PLEX_SERVICE_NAME_USERNAME, username)
        keyring.set_password(PLEX_SERVICE_NAME, username, token)
        return account


def get_runtime_left(show: Show) -> int | float:
    episodes = cast(List[Episode], show.unwatched())
    total_runtime = 0
    for episode in tqdm(episodes, desc="Calculating runtime left"): 

        # calculate intro and credit duration and subtract it from
        # the total runtime since it's not part of the actual episode
        markers = cast(List[Marker], episode.markers)
        intro_and_credit_duration = 0
        for marker in markers:
            if marker.type == 'intro' or marker.type == 'credits':
                intro_and_credit_duration += marker.end - marker.start 

        total_runtime += episode.duration - intro_and_credit_duration
    return total_runtime

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get runtime left in anything in series')
    parser.add_argument('--overwrite-token', '-O', default=False, action=argparse.BooleanOptionalAction, help='Overwrite the token in the keyring')
    args = parser.parse_args()

    account = handle_plex_authentication(args.overwrite_token) 
    
    plexserver = cast(PlexServer, account.resource('AbdallahNAS').connect())

    while True:
        libraries = cast(List[LibrarySection], plexserver.library.sections())
        libraries = [library for library in libraries if library.type == 'show']
        library_titles = [library.title for library in libraries]
        library_title = iterfzf(library_titles, prompt='Select library: ')
        library = cast(ShowSection, libraries[library_titles.index(library_title)])

        shows = library.all()

        show_titles = [show.title for show in shows]
        show_title = iterfzf(show_titles, prompt='Select item: ')
        show = cast(Show, shows[show_titles.index(show_title)])
        
        runtime_left = get_runtime_left(show)
        runtime_left_duration = datetime.timedelta(milliseconds=runtime_left)

        print(f'Runtime left: {runtime_left_duration}')

        user_input = input('Do you want to select another item? [Y/n]: ') 
        while user_input not in ['y', 'Y', 'n', 'N', '']:
            user_input = input("Please enter 'y' or 'n': ")

        if user_input == 'n' or user_input == 'N':
            break

