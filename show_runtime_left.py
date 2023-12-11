#!/usr/bin/env python

from typing import TypeAlias, cast, List, Tuple
from plexapi.media import Marker
from plexapi.server import PlexServer
from plexapi.library import LibrarySection, MovieSection, ShowSection 
from plexapi.video import Movie, Show, Episode
from iterfzf import iterfzf
from tqdm import tqdm
import datetime
from authenticate_plex import handle_plex_authentication
import argparse
from concurrent.futures import ThreadPoolExecutor

for includeKey in Episode._INCLUDES:
    Episode._INCLUDES[includeKey] = 0
Episode._INCLUDES['includeMarkers'] = 1 

RuntimeLeft: TypeAlias = Tuple[int, int]

def clear_screen() -> None:
    print('\033[H\033[J')

def reload_episode(episode: Episode) -> Episode:
    return episode.reload()

def get_series_runtime_left(show: Show, skip_markers: bool = False, should_print: bool = True, max_marker_workers: int | None = None) -> RuntimeLeft:
    unwatched_episodes = cast(List[Episode], show.unwatched())

    if not skip_markers:
        with ThreadPoolExecutor(max_workers=max_marker_workers) as executor:
            if should_print:
                 list(tqdm(executor.map(reload_episode, unwatched_episodes), total=len(unwatched_episodes), desc=f'Fetching episode markers for "{show.title}"'))
            else:
                 list(executor.map(reload_episode, unwatched_episodes))

    total_runtime_with_watched = 0
    for episode in tqdm(show.episodes(), desc=f'Calculating total runtime with watched for "{show.title}"') if should_print else show.episodes():
        total_runtime_with_watched += episode.duration


    total_runtime_without_watched = 0

    total_intro_and_credit_duration = 0
    if unwatched_episodes.__len__() == 0 and should_print:
        print(f'All episodes are already watched for "{show.title}".')
        print("Skipping calculation of runtime left...")
    else:
        for episode in tqdm(unwatched_episodes, desc=f'Calculating runtime left for "{show.title}"') if should_print else unwatched_episodes: 

            if not skip_markers:
                ## Add to the total intro and credit duration which will later be subtracted from the runtime left
                markers = [marker for marker in episode.markers if marker.type == 'intro' or marker.type == 'credit']
                markers = cast(List[Marker], markers)
                for marker in markers: 
                    marker_duration = marker.end - marker.start
                    total_intro_and_credit_duration += marker_duration

            total_runtime_without_watched += episode.duration
        total_runtime_without_watched -= total_intro_and_credit_duration

    return (int(total_runtime_with_watched), int(total_runtime_without_watched))

def get_movie_runtime_left(movie: Movie, skip_markers: bool = False) -> RuntimeLeft:

    total_runtime_with_watched = movie.duration
    total_runtime_without_watched = movie.duration

    if not skip_markers:
        ## Add to the total intro and credit duration which will later be subtracted from the runtime left
        markers = [marker for marker in movie.markers if marker.type == 'intro' or marker.type == 'credit']
        markers = cast(List[Marker], markers)
        total_intro_and_credit_duration = 0
        for marker in markers: 
            marker_duration = marker.end - marker.start
            total_intro_and_credit_duration += marker_duration
        total_runtime_without_watched -= total_intro_and_credit_duration

    return (int(total_runtime_with_watched), int(total_runtime_without_watched))

def get_library_runtime_left(library: LibrarySection, entire_library: bool, skip_markers: bool) -> RuntimeLeft:
        resulting_runtime_left: RuntimeLeft = (0, 0)

        if library.type == 'show':
            library = cast(ShowSection, library)
            shows = library.all()

            if not entire_library:
                # Select show
                show_titles = [show.title for show in shows]
                show_title = None
                show_title = iterfzf(show_titles, prompt='Select item: ', case_sensitive=False)

                show = cast(Show, shows[show_titles.index(show_title)])
                resulting_runtime_left = get_series_runtime_left(show, skip_markers) 
            else:
                # Start incrementing the total runtime and runtime left
                for show in tqdm(shows, desc="Calculating runtime left for all shows"):
                    # we don't want to get network blocked since we are checking many shows so the max_workers is set to 2
                    # not necessary when only checking for one show since server not likely to block us for that
                    runtime_left = get_series_runtime_left(show, skip_markers, should_print=False, max_marker_workers=2)
                    resulting_runtime_left = (resulting_runtime_left[0] + runtime_left[0], resulting_runtime_left[1] + runtime_left[1])

        elif library.type == 'movie':
            library = cast(MovieSection, library)
            movies = library.all()

            # Start incrementing the total runtime and runtime left
            for movie in tqdm(movies, desc="Calculating runtime left for all movies"):
                runtime_left = get_movie_runtime_left(movie, skip_markers)
                resulting_runtime_left = (resulting_runtime_left[0] + runtime_left[0], resulting_runtime_left[1] + runtime_left[1])

        return resulting_runtime_left

def print_runtime_left(runtime_left: RuntimeLeft) -> None:
    print('\n')
    print(f'Total runtime: {datetime.timedelta(milliseconds=runtime_left[0])}')
    print(f'Runtime left: {datetime.timedelta(milliseconds=runtime_left[1])}')
    print('\n')

def isYes(input):
    return input == 'y' or input == 'Y'

def isNo(input):
    return input == 'n' or input == 'N'

valid_responses = ['y', 'Y', 'n', 'N', '']

if __name__ == '__main__':
    args = argparse.ArgumentParser(description='Calculate the runtime left of a show.')
    args.add_argument('-o', '--overwrite-token', default=False, action='store_true', help='Overwrite the stored token in the keyring.')
    args.add_argument('-e', '--entire-library', default=False, action='store_true', help='Calculate the runtime left of all shows in the library.')
    args.add_argument('-s', '--skip-markers', default=False, action='store_true', help='Proceed without the additional calculations for markers.')
    parsed_args = args.parse_args()

    overwrite_token = parsed_args.overwrite_token
    entire_library = parsed_args.entire_library
    skip_markers = parsed_args.skip_markers

    account = handle_plex_authentication(overwrite_token) 
    
    server_name = None
    if len(account.resources()) == 1:
        server_name = account.resources()[0].name
    else:
        server_names = [server.name for server in account.resources()]
        server_name = None
        server_name = iterfzf(server_names, prompt='Select server: ', case_sensitive=False)

    plexserver = cast(PlexServer, account.resource(server_name).connect())

    while True:
        clear_screen()
        libraries = cast(List[LibrarySection], plexserver.library.sections())
        libraries = [library for library in libraries if library.type == 'show' or library.type == 'movie']

        # Select library
        library_titles = [library.title for library in libraries]
        library_title = None
        
        library_title = iterfzf(library_titles, prompt='Select library: ', case_sensitive=False)
        library = libraries[library_titles.index(library_title)]

        runtime_left = get_library_runtime_left(library, entire_library, skip_markers)
        print_runtime_left(runtime_left)

        user_input = input('Do you want to select another item? [Y/n]: ') 
        while user_input not in valid_responses:
            user_input = input("Please enter 'y' or 'n': ")

        print('\n')
        if isNo(user_input):
            break


