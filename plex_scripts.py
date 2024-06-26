import argparse
import authenticate_plex
import show_runtime_left
import push_to_recently_added

if __name__ == '__main__':

    # main parser
    parser = argparse.ArgumentParser(prog="plex_scripts", description='A collection of scripts to interact with Plex.')
    parser.add_argument('-o', '--overwrite-token', default=False, action='store_true', help='Overwrite the stored token in the keyring.')

    subparsers = parser.add_subparsers(dest='script_name', required=True)

    show_runtime_left_name = show_runtime_left.add_arguments(subparsers)
    push_to_recently_added_name = push_to_recently_added.add_arguments(subparsers)

    kwargs = vars(parser.parse_args())
    script_name = kwargs.pop('script_name')

    account = authenticate_plex.handle_plex_authentication(kwargs.pop('overwrite_token'))

    if script_name == show_runtime_left_name:
        show_runtime_left.run(account, **kwargs)
    elif script_name == push_to_recently_added_name:
        push_to_recently_added.run(account, **kwargs)
    else:
        print(f'Unknown script name: {script_name}')
        parser.print_help()
        exit(1)

