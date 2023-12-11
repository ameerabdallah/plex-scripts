from plexapi.myplex import MyPlexAccount
import keyring
import getpass
from typing import cast

PLEX_SERVICE_NAME = "plex_api"
PLEX_SERVICE_NAME_USERNAME = "plex_api_username"
PLEX_SERVICE_NAME_SERVERNAME = "plex_api_servername"

def handle_plex_authentication(overwrite_token: bool) -> MyPlexAccount:
    """
    Handles the authentication for plex. If the token is already stored in the keyring, it will use that. 
    Otherwise, it will prompt for username and password and store the token in the keyring.
    """

    credentials = None
    username = None
    if overwrite_token == False:
        username = keyring.get_password(PLEX_SERVICE_NAME, PLEX_SERVICE_NAME_USERNAME)
        credentials = keyring.get_credential(PLEX_SERVICE_NAME, username)

    if credentials is not None:
        token = cast(str, credentials.password)

        try:
            plex_account = MyPlexAccount(username=username, token=token)
        except:
            print("Token is invalid. Please reauthenticate.")
            plex_account = handle_plex_authentication(True)

        return plex_account
    else:
        username = input("Username: ")
        password = getpass.getpass(f'Password for {username}: ')
        account = MyPlexAccount(username, password)
        token = account.authenticationToken
        keyring.set_password(PLEX_SERVICE_NAME, PLEX_SERVICE_NAME_USERNAME, username)
        keyring.set_password(PLEX_SERVICE_NAME, username, token)
        return account

