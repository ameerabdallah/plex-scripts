#!/usr/bin/env python

from typing import cast, List, Tuple
from plexapi.media import Marker
from plexapi.server import PlexServer
from plexapi.library import LibrarySection, ShowSection 
from plexapi.video import Show, Episode
from iterfzf import iterfzf
from tqdm import tqdm
import datetime
from authenticate_plex import handle_plex_authentication
import argparse
from concurrent.futures import ThreadPoolExecutor

for includeKey in Episode._INCLUDES:
    Episode._INCLUDES[includeKey] = 0
Episode._INCLUDES['includeMarkers'] = 1 

def reload_episode(episode: Episode) -> Episode:
    return episode.reload()

def get_runtime_left(show: Show) -> Tuple[int, int]:

    unwatched_episodes = cast(List[Episode], show.unwatched())
    with ThreadPoolExecutor() as executor:
        list(tqdm(executor.map(reload_episode, unwatched_episodes), total=len(unwatched_episodes), desc="Fetching episode markers. This may take a while."))

    total_runtime_with_watched = 0
    for episode in tqdm(show.episodes(), desc="Calculating total runtime with watched"):
        total_runtime_with_watched += episode.duration


    total_runtime_without_watched = 0

    total_intro_and_credit_duration = 0
    if unwatched_episodes.__len__() == 0:
        print("All episodes are already watched for this series...")
        print("Skipping calculation of runtime left...")
    else:
        for episode in tqdm(unwatched_episodes, desc="Calculating runtime left"): 

            ## Add to the total intro and credit duration which will later be subtracted from the runtime left
            markers = [marker for marker in episode.markers if marker.type == 'intro' or marker.type == 'credit']
            markers = cast(List[Marker], markers)
            for marker in markers: 
                marker_duration = marker.end - marker.start
                total_intro_and_credit_duration += marker_duration

            total_runtime_without_watched += episode.duration
        total_runtime_without_watched -= total_intro_and_credit_duration

    return (total_runtime_with_watched, int(total_runtime_without_watched))

def isYes(input):
    return input == 'y' or input == 'Y'

def isNo(input):
    return input == 'n' or input == 'N'

valid_responses = ['y', 'Y', 'n', 'N', '']

if __name__ == '__main__':
    args = argparse.ArgumentParser(description='Calculate the runtime left of a show.')
    args.add_argument('--overwrite-token', '-O', default=False, action='store_true', help='Overwrite the stored token in the keyring.')
    parsed_args = args.parse_args()

    account = handle_plex_authentication(parsed_args.overwrite_token) 
    
    server_name = None
    if len(account.resources()) == 1:
        server_name = account.resources()[0].name
    else:
        server_name = iterfzf([server.name for server in account.resources()], prompt='Select server: ')

    plexserver = cast(PlexServer, account.resource(server_name).connect())

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

        print('\n')
        print(f'Total runtime: {datetime.timedelta(milliseconds=runtime_left[0])}')
        print(f'Runtime left: {datetime.timedelta(milliseconds=runtime_left[1])}')
        print('\n')

        user_input = input('Do you want to select another item? [Y/n]: ') 
        while user_input not in valid_responses:
            user_input = input("Please enter 'y' or 'n': ")

        print('\n')
        if isNo(user_input):
            break


