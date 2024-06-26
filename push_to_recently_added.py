import argparse
import time
from typing import List
from plexapi.myplex import MyPlexAccount
from plexapi.video import Episode, Movie, Season, Show
from get_plex_objects import prompt_for_episode, prompt_for_movie, prompt_for_season, prompt_for_server, prompt_for_library, prompt_for_show

specificity_choices = ['movie', 'show', 'season', 'episode']
PUSH_TO_RECENTLY_ADDED_NAME = 'push-recently-added'
def add_arguments(subparser: argparse._SubParsersAction):
    parser: argparse.ArgumentParser  = subparser.add_parser(PUSH_TO_RECENTLY_ADDED_NAME, description='Push a show to recently added by update the date added attribute.')
    parser.add_argument(dest='specificity', choices=specificity_choices, help='The specificity of the item to push to recently added.')
    return PUSH_TO_RECENTLY_ADDED_NAME

specificity_show_type = ['show', 'season', 'episode']
def run(account: MyPlexAccount, **kwargs):
    server = prompt_for_server(account)
    specificity = kwargs['specificity']

    media = None
    if specificity in specificity_show_type:
        library = prompt_for_library(server, library_types=['show'])
        if specificity == 'show':
            push_show_to_recently_added(prompt_for_show(library))
        elif specificity == 'season':
            show = prompt_for_show(library)
            media = prompt_for_season(show)
        elif specificity == 'episode':
            show = prompt_for_show(library)
            season = prompt_for_season(show)
            media = prompt_for_episode(season)
    elif specificity == 'movie':
        library = prompt_for_library(server, library_types=['movie'])
        media = prompt_for_movie(library)
    else:
        raise ValueError(f'Unknown specificity: {specificity}')

    push_to_recently_added(media)

def push_to_recently_added(media: Movie | Episode | Season | Show | None, current_time: int = int(time.time())):
    if media is None:
        return

    if isinstance(media, Movie) or isinstance(media, Episode):
        push_video_to_recently_added(media, current_time)
    elif isinstance(media, Season):
        push_season_to_recently_added(media, current_time)
    elif isinstance(media, Show):
        push_show_to_recently_added(media, current_time)
    else:
        raise ValueError(f'Unknown video type: {type(media)}')


def push_video_to_recently_added(video: Movie | Episode, current_time: int = int(time.time())):
    if isinstance(video, Episode):
        print(f'Pushing S{video.seasonNumber}E{video.episodeNumber}: {video.title} to recently added.')
    video.batchEdits()
    video.editAddedAt(current_time).editField('updatedAt', current_time)
    video.saveEdits()



def push_season_to_recently_added(season: Season, current_time: int = int(time.time())):
    print(f'Pushing {season.title} to recently added.')
    season.batchEdits()
    season.editAddedAt(current_time).editField('updatedAt', current_time)
    episodes: List[Episode] = season.episodes()
    for episode in episodes:
        push_to_recently_added(episode, current_time)
    season.saveEdits()


def push_show_to_recently_added(show: Show, current_time: int = int(time.time())):
    show.batchEdits()
    show.editAddedAt(current_time).editField('updatedAt', current_time)
    seasons: List[Season] = show.seasons()
    for season in seasons:
        push_season_to_recently_added(season, current_time)
    show.saveEdits()
