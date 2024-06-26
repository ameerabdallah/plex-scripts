from iterfzf import iterfzf
from plexapi.myplex import LibrarySection, MyPlexAccount, MyPlexResource, PlexServer
from plexapi.video import Episode, Movie, Season, Show


def clear_screen() -> None:
    print("\033[H\033[J")


def prompt_for_server(account: MyPlexAccount) -> PlexServer:
    resource: MyPlexResource
    resources = account.resources()
    print("Querying Plex servers...")
    if len(resources) == 1:
        resource = resources[0]
    else:
        resource_names = [resource.name for resource in resources]
        resource_name = iterfzf(resource_names, prompt="Select server: ", case_sensitive=False)
        resource = resources[resource_names.index(resource_name)]
    return resource.connect()


def prompt_for_library(plexserver: PlexServer, library_types=['show', 'movie']) -> LibrarySection:
    clear_screen()
    libraries = plexserver.library.sections()
    libraries = [library for library in libraries if library.type in library_types]
    library_titles = [library.title for library in libraries]
    library_title = iterfzf(library_titles, prompt="Select library: ", case_sensitive=False)
    return libraries[library_titles.index(library_title)]

def prompt_for_show(library: LibrarySection) -> Show:
    shows = library.all()
    show_titles = [show.title for show in shows]
    show_title = iterfzf(show_titles, prompt='Select show: ', case_sensitive=False)
    return shows[show_titles.index(show_title)]

def prompt_for_season(show: Show) -> Season:
    seasons = show.seasons()
    season_titles = [season.title for season in seasons]
    season_title = iterfzf(season_titles, prompt='Select season: ', case_sensitive=False)
    return seasons[season_titles.index(season_title)]

def prompt_for_episode(season: Season) -> Episode:
    episodes = season.episodes()
    episode_titles = [episode.title for episode in episodes]
    episode_title = iterfzf(episode_titles, prompt='Select episode: ', case_sensitive=False)
    return episodes[episode_titles.index(episode_title)]

def prompt_for_movie(library: LibrarySection) -> Movie:
    movies = library.all()
    movie_titles = [movie.title for movie in movies]
    movie_title = iterfzf(movie_titles, prompt='Select movie: ', case_sensitive=False)
    return movies[movie_titles.index(movie_title)]

