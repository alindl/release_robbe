"""

Get and manage new songs and artists from Spotify

:Author: Andreas Lindlbauer (@alindl)
:Copyright: (c) 2021 Andreas Lindlbauer

"""

__license__ = "EUPL"
__docformat__ = 'reStructuredText'

import difflib
import subprocess
import math
import os.path
import sys
from enum import Enum
import pygame
from dialog import Dialog
import spotipy
import spotipy.util as util
import file_interaction as fi
import config_io as conf

# Currently set to 28 Aug 2020


class States(Enum):
    """

    Enum to represent the different states

    """
    START = "START"
    EXIT = "EXIT"
    DONE = "DONE"
    NEW_RELEASES = "NR"
    TOP_10_GREY = "TG"
    CONF = "CONF"
    DATE = "DATE"
    LISTS = "LISTS"
    ALLOWLIST = "AL"
    GREYLIST = "GL"
    BLOCKLIST = "BL"
    POP_GREY = "PG"
    SOURCE = "SOURCE"
    # NOTE Using int would improve performance, but result in worse legibility


DIALOG = Dialog(dialog="dialog")
ARTISTS_SET = set()
ARTISTS_DICT = {}
ALL_SONGS = set()
LIST_DICT = {
    fi.Lists.ALLOWLIST.value:  fi.Lists.ALLOWLIST,
    fi.Lists.GREYLIST.value:  fi.Lists.GREYLIST,
    fi.Lists.BLOCKLIST.value:  fi.Lists.BLOCKLIST,
    fi.Lists.DELETE.value:  fi.Lists.DELETE
    }

def main():
    """

    One function to start them all

    """
    if os.path.isfile('mach_die_robbe.mp3'):
        pygame.mixer.init()
        pygame.mixer.music.load("mach_die_robbe.mp3")
        pygame.mixer.music.play(-1)

    state = States.START
    while True:
        while state not in (States.NEW_RELEASES, States.TOP_10_GREY):
            state = menu(state)
            if state == States.EXIT:
                #clear_screen()
                sys.exit()

        scope = 'playlist-read-collaborative \
                 playlist-read-private \
                 playlist-modify-private \
                 playlist-modify-public \
                 user-follow-read'
        token = util.prompt_for_user_token(conf.get_key('Auth', 'username'), scope,
                                           client_id=conf.get_key('Auth', 'client_id'),
                                           client_secret=conf.get_key('Auth', 'client_secret'),
                                           redirect_uri='http://localhost:8888/callback/')
        if token:

            spot_conn = spotipy.Spotify(auth=token)
            #spot_conn.trace = False

            fi.sort_all_lists(DIALOG)

            get_songs(spot_conn, state)

            if not add_songs_to_playlist(spot_conn):
                DIALOG.msgbox("Something didn't go right, while adding songs to your playlist")
            else:
                conf.write_time()
                DIALOG.msgbox("Done!")

            state = States.START
            clear_screen()

            fi.sort_all_lists(DIALOG)
        else:
            print("Can't get token for", conf.get_key('Auth', 'username'))

        clear_screen()

def start_menu():
    """

    Main menu

    """
    text = """
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　████████████          
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　██░░░░░░░░░░░░██        
　　 ░█▀▀█ █▀▀ █── █▀▀ █▀▀█ █▀▀ █▀▀ 　 ░█▀▀█ █▀▀█ █▀▀▄ █▀▀▄ █▀▀　　　　 ██░░░░░░░░░░░░░░░░██      
　　 ░█▄▄▀ █▀▀ █── █▀▀ █▄▄█ ▀▀█ █▀▀ 　 ░█▄▄▀ █──█ █▀▀▄ █▀▀▄ █▀▀　　　 ██░░░░ 　 ░░░░░░ 　 ░░██    
　　 ░█─░█ ▀▀▀ ▀▀▀ ▀▀▀ ▀──▀ ▀▀▀ ▀▀▀ 　 ░█─░█ ▀▀▀▀ ▀▀▀─ ▀▀▀─ ▀▀▀　　　 ██░░░░　██░░░░░░██　░░██    
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　██░░░░　██░░░░░░██　░░██    
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　██░░░░░░░░░░██░░░░░░░░██    
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　██░░░░████░░░░░░████░░██    
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　██░░░░██░░░░░░██░░░░░░██      
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　██████████░░░░░░░░████░░░░░░████        
　　　　　　　　　　　　　　　　　　　　　　　　　　　　██░░░░░░██░░░░░░░░██░░░░░░░░░░██　██      
　　　　　　　　　　　　　　　　　　　　　　　　　　　██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██        
　　　　　　　　　　　　　　　　　　　　　　　　　　██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██        
　　　　　　　　　　　　　　　　　　　　████████　██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██          
　　　　　　　　　　　　　　　　　　　██░░░░░░░░████░░░░░░░░░░░░░░░░██░░░░░░░░░░░░░░░░██████      
　　　　　　　　　　　　　　　　　　██░░░░██░░░░░░░░░░░░░░░░░░░░░░░░██░░░░░░░░░░██░░██░░░░░░████  
　　　　　　　　　　　　　　　　　　　████░░░░░░░░░░██░░░░░░░░░░░░██░░░░░░░░░░██░░██░░░░░░██░░░░██
　　　　　　　　　　　　　　　　　　██░░░░░░░░░░░░██████░░░░░░░░██████░░░░░░░░████　████░░░░░░░░██
　　　　　　　　　　　　　　　　　　　████████████　　　██████████░░░░░░░░░░██　　　　　████████  
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　██████████                      
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　
"""

    choices = [(States.NEW_RELEASES.value,
                "Get new releases"),
               (States.TOP_10_GREY.value,
                "Fetch top 10 of all artists on greylist"),
               (States.CONF.value,
                "Configure credentials"),
               (States.POP_GREY.value,
                "Decide on Greylist entries (to allow/block-list or delete)"),
               (States.DATE.value,
                "Set start date to check releases from"),
               (States.LISTS.value,
                "View/Edit List (Allow, Grey, Block)"),
               (States.SOURCE.value,
                "Modify source of artists (playlist/allowlist/following)"),
               (States.EXIT.value,
                "Quit")]
    code, state = DIALOG.menu(text, choices=choices, no_tags=True,
            no_cancel=True, height=39, width=108, tab_len=1)
    if code != DIALOG.OK:
        return States.EXIT
    return States(state)

def rel_menu():
    """
    Start going for new releases from artists from your source.
    Also check if source was set

    """
    conf_set, _ = conf.get_credentials()
    if conf_set:
        if not conf.get_key('Other', 'source'):
            return States.SOURCE
        return States.NEW_RELEASES
    return States.CONF

def top_menu():
    """
    Pick top 10 releases from all artists of your greylist.

    """
    conf_set, _ = conf.get_credentials()
    if conf_set:
        return States.TOP_10_GREY
    return States.CONF

def date_menu():
    """
    Menu to pick a day, that will be used to get releases from there to today.

    """
    # NOTE Weird way to say that
    last_check = conf.read_time()
    code, date = DIALOG.calendar("From which date on do you want to add releases?",
                                 day=last_check.day,
                                 month=last_check.month,
                                 year=last_check.year,
                                 title="Configure checking date")

    if code == DIALOG.OK:
        conf.set_key('Other', 'last_check', str(conf.convert_list_to_ts(date)))
    return States.START

def do_exit():
    """
    Exit programm, but clear screen just before that

    """
    clear_screen()
    return States.EXIT

def menu(state):
    """

    Menu to check all configs

    """

    if state == States.START:
        output = start_menu()
    elif state == States.NEW_RELEASES:
        output = rel_menu()
    elif state == States.TOP_10_GREY:
        output = top_menu()
    elif state == States.CONF:
        output = configure_prog()
    elif state == States.DATE:
        output = date_menu()
    elif state == States.LISTS:
        output = list_chooser()
    elif state == States.POP_GREY:
        output = edit_chooser(fi.Lists.GREYLIST, States.POP_GREY)
    elif state == States.SOURCE:
        output = source_chooser()
    else:
        output = do_exit()
    return output

    # Somehow, pylint doesn't like my switch-case implementation, too many lambdas
    #switcher = {
    #    States.START: lambda: start_menu(),
    #    States.NEW_RELEASES: lambda: rel_menu(),
    #    States.TOP_10_GREY: lambda: top_menu(),
    #    States.CONF: lambda: configure_prog(),
    #    States.DATE: lambda: date_menu(),
    #    States.LISTS: lambda: list_chooser(),
    #    States.POP_GREY: lambda: edit_chooser(fi.Lists.GREYLIST, States.POP_GREY),
    #    States.SOURCE: lambda: source_chooser()
    #         }
    #return switcher.get(state, lambda : do_exit())()

def source_chooser():
    """

    Choose which source to get artists from

    """
    text = """ Where should the artists come from? """
    code, source = DIALOG.menu(text, choices=[("playlists", "Chosen Playlists"),
                                              ("allowlist", "Allowlist"),
                                              ("saved", "Artists I follow")], no_tags=True)

    if code == DIALOG.OK:
        conf.set_key('Other', 'source', source)
    return States.START


def list_and_push_artists(from_list):
    """

    Get whole list and decide on artists

    """
    choices = []
    artists, size_of_list = fi.get_list(from_list)
    if size_of_list < 1:
        DIALOG.msgbox("List is empty.")
        return False

    for i, artist in enumerate(artists):
        #artist = artists[i]
        if isinstance(artist, list):
            choices.append((str(i), artist[0], False))
        else:
            choices.append((str(i), artist, False))
    text = "Which artists would you like to push from %s" % (from_list.name)
    code, tags = DIALOG.checklist(text=text, cancel_label="Back",
                                  choices=choices, no_tags=True)

    if code == DIALOG.OK:
        text = "Where should these artists be pushed to?"
        choices = [(fi.Lists.ALLOWLIST.value, "Push to Allowlist "),
                   (fi.Lists.BLOCKLIST.value, "Push to Blocklist"),
                   (fi.Lists.DELETE.value, "Push into /dev/null")]
        for choice in choices:
            if choice[0] == from_list.value:
                choices.remove(choice)
        code, to_list = DIALOG.menu(text, choices=choices,
                                    cancel_label="Abort",
                                    no_tags=True)
    else:
        return True

    if code == DIALOG.OK:
        to_list = LIST_DICT[to_list]
        for i in tags:
            fi.move_artist_between_lists(from_list, to_list, artists[int(i)])
        return True
    return False



def search_and_push_artist(from_list):
    """

    Give name of specific artist,
    - Look up entry from list.
    - If found decide on fate
    - If not found, maybe get whole list or try again?

    """
    text = """ Name of artist """
    entry = None
    code, artist = DIALOG.inputbox(text, cancel_label="Abort")

    if code == DIALOG.OK:
        entry = fi.check_if_on_list(from_list, [artist])
    else:
        return True

    if entry:
        text = """ Found %s! Where should this artist go to? """ % (entry[0])
        choices = [(fi.Lists.ALLOWLIST.value, "Push to Allowlist "),
                   (fi.Lists.BLOCKLIST.value, "Push to Blocklist"),
                   (fi.Lists.DELETE.value, "Push into /dev/null")]
        for choice in choices:
            if choice[0] == from_list.value:
                choices.remove(choice)
        code, to_list = DIALOG.menu(text, choices=choices,
                                    cancel_label="Abort",
                                    no_tags=True)
        if code == DIALOG.OK:
            to_list = LIST_DICT[to_list]
            if fi.move_artist_between_lists(from_list, to_list, entry):
                return True
    return False


def edit_chooser(from_list, referrer):
    """

    Choose how to edit the list

    """
    text = """ Do you have a specific artist in mind or \
            do you want to check the whole %s? """ % (from_list.name)
    code, tag = DIALOG.menu(text, choices=[("specific", "Specific artist"),
                                           ("list", "Whole list")], no_tags=True)

    while code == DIALOG.OK:
        if tag == "specific":
            if not search_and_push_artist(from_list):
                return referrer

        if tag == "list":
            if not list_and_push_artists(from_list):
                return referrer

        code, tag = DIALOG.menu(text, choices=[("specific", "Specific artist"),
                                               ("list", "Whole list")],
                                cancel_label="Back", no_tags=True)
    if referrer == States.POP_GREY:
        return States.START
    return States.LISTS



def list_chooser():
    """

    Choose which list to view/edit

    """
    text = """ Which list do you want to edit? """
    code, from_list = DIALOG.menu(text, choices=[(fi.Lists.ALLOWLIST.value, "Allowlist"),
                                                 (fi.Lists.GREYLIST.value, "Greylist"),
                                                 (fi.Lists.BLOCKLIST.value, "Blocklist")],
                                  no_tags=True)
    if code == DIALOG.OK:
        from_list = LIST_DICT[from_list]
        return edit_chooser(from_list, States.LISTS)

    return States.START


def configure_prog():
    """

    Edit Spotify credentials

    """
    _, info = conf.get_credentials()
    valid, error_msg, add_height = conf.check_credentials(info)

    elements = [
        ("Username", 1, 1,
         info[0] if info[0] else "xXspice_girls_4_lifeXx",
         1, 20, 32, 32),
        ("Client ID", 2, 1,
         info[1] if info[1] else "some32alphanumericcharacters",
         2, 20, 32, 32),
        ("Client Secret", 3, 1,
         info[2] if info[2] else "other32alphanumericcharacters",
         3, 20, 32, 32),
        ("Country", 4, 1,
         info[3] if info[3] else "US",
         4, 20, 10, 2),
        ("Allowlist", 5, 1,
         info[4] if info[4] else "allowlist.csv",
         5, 20, 32, 32),
        ("Greylist", 6, 1,
         info[5] if info[5] else "greylist.csv",
         6, 20, 32, 32),
        ("Blocklist", 7, 1,
         info[6] if info[6] else "whitelist.csv",
         7, 20, 32, 32)
        ]

    height = 14 + add_height
    code, fields = DIALOG.form("Please fill in your Spotify credentials:" + error_msg,
                               elements, width=80, height=height)

    if code != DIALOG.OK:
        return States.START

    valid, error_msg, add_height = conf.check_credentials(fields)
    height = 14 + add_height

    while not valid:
        elements = [
            ("Username", 1, 1, fields[0], 1, 20, 32, 32),
            ("Client ID", 2, 1, fields[1], 2, 20, 32, 32),
            ("Client Secret", 3, 1, fields[2], 3, 20, 32, 32),
            ("Country", 4, 1, fields[3], 4, 20, 10, 2),
            ("Allowlist", 5, 1, fields[4], 5, 20, 32, 32),
            ("Greylist", 6, 1, fields[5], 6, 20, 32, 32),
            ("Blocklist", 7, 1, fields[6], 7, 20, 32, 32)
            ]
        code, fields = DIALOG.form("Please fill in your Spotify credentials:" + error_msg,
                                   elements, width=80, height=height)
        if code != DIALOG.OK:
            return States.START

        valid, error_msg, add_height = conf.check_credentials(fields)
        height = 14 + add_height

    if code == DIALOG.OK:
        conf.set_key('Auth', 'username', fields[0])
        conf.set_key('Auth', 'client_id', fields[1])
        conf.set_key('Auth', 'client_secret', fields[2])
        conf.set_key('Other', 'country', fields[3])
        conf.set_key('Lists', 'allowlist', fields[4])
        conf.set_key('Lists', 'greylist', fields[5])
        conf.set_key('Lists', 'blocklist', fields[6])

    return States.START


def check_and_get_artist_id(spot_conn, name):
    """

    Get artist id from Spotify

    """
    results = None
    if isinstance(name, str):
        results = spot_conn.search(q=name, type='artist')
    elif isinstance(name, list):
        if len(name) == 1:
            results = spot_conn.search(q=name[0], type='artist')
        elif len(name) == 2:
            return name[1]
        else:
            return None
    else:
        return None

    items = results['artists']['items']
    if len(items) > 0:
        return items[0]['id']
    return None


def buzz_filter(string):
    """
    Filter out strings containing buzz words, except for the ones having anti_buzz words
    """
    buzzwords = ['LIVE', '- Live', '(Live']
    buzzwords_lowercase = ['(live', ' - live', ' live version',
                           ' live from', ' live in', ' live at', 'instrumental',
                           'interlude', 'acoustic']
    anti_buzzwords = ['RAC']
    anti_buzzwords_lowercase = ['rac']

    # Contains any buzzword from the list
    has_buzzwords = any(buzz in string for buzz in buzzwords)

    # Contains any anti buzzword from the list that would allow the use of a buzzword
    has_anti_buzzwords = any(anti_buzz in string for anti_buzz in anti_buzzwords)

    # Same for case-insensitive buzzwords.
    has_lowercase_buzzwords = any(buzz in string.lower() for buzz in buzzwords_lowercase)
    has_lowercase_anti_buzzwords = any(anti_buzz in string.lower() \
            for anti_buzz in anti_buzzwords_lowercase)

    return (not has_buzzwords or has_anti_buzzwords ) and \
           (not has_lowercase_buzzwords or has_lowercase_anti_buzzwords)

def get_album_tracks(spot_conn, album, track_names, track_uris):
    """

    Get all tracks from album ID

    """
    tracks = []
    num_tracks = 0
    track_page = spot_conn.album_tracks(album['id'], limit=10)

    tracks.extend(track_page['items'])

    while track_page['next']:
        track_page = spot_conn.next(track_page)
        tracks.extend(track_page['items'])
    for track in tracks:
        track_name = track['name']
        if buzz_filter(track_name):
            track_names.append(track_name)
            track_uris.append(track['uri'])
            ALL_SONGS.add(track['uri'])
            num_tracks += 1
    return num_tracks
    # NOTE How to filter remixes, if the remixer isn't the artist?

def get_artist_albums(spot_conn, artist_id):
    """

    Get all albums from artist ID

    """
    albums = []
    album_page = spot_conn.artist_albums(artist_id, album_type='album,single', limit=10)
    albums.extend(album_page['items'])
    while album_page['next']:
        album_page = spot_conn.next(album_page)
        albums.extend(album_page['items'])
    return albums


def delete_duplicate_songs(track_names, track_uris):
    """

    Remove duplicate songs

    """
    duplicates = 0
    for track_first_idx in enumerate(track_names):
        for track_second_idx in range(track_first_idx[0], len(track_uris)):
            if track_first_idx[0] != track_second_idx:
                seq = difflib.SequenceMatcher(a=track_names[track_first_idx[0]].lower(),
                                              b=track_names[track_second_idx].lower())
                if seq.ratio() > 0.9:
                    if track_uris[track_second_idx] in ALL_SONGS:
                        ALL_SONGS.remove(track_uris[track_second_idx])
                        duplicates += 1
    return duplicates


def check_artist_albums(spot_conn, artist_info):
    """

    Go through all album tracks of artists

    """
    num_tracks = 0
    track_names = []
    track_uris = []
    albums = get_artist_albums(spot_conn, artist_info[1])
    #i = 0
    #DIALOG.gauge_start(text="Gathering songs by %s ..." % (artist_info[0]), percent=0)
    #total_albums = len(albums)

    unique = set()  # skip duplicate albums
    for album in albums:
        #DIALOG.gauge_update(math.floor((i/total_albums)*100))
        album_name = album['name']
        if album_name not in unique and album['album_type'] != 'compliation':
            if conf.get_release_date(album) > conf.read_time():
                num_tracks += get_album_tracks(spot_conn, album, track_names, track_uris)

            unique.add(album_name)
        #i += 1
    #DIALOG.gauge_stop()
    num_tracks -= delete_duplicate_songs(track_names, track_uris)
    return num_tracks


def get_user_playlists(spot_conn):
    """

    Gets a list of playlist information of all user playlists
    Saved playlists from other people also get added

    """
    playlists_page = spot_conn.current_user_playlists()

    playlists = []

    for playlist in playlists_page['items']:
        playlists.append({'name': playlist['name'],
                          'owner': playlist['owner'],
                          'id': playlist['id']})

    while playlists_page['next']:
        playlists_page = spot_conn.next(playlists_page)
        for playlist in playlists_page['items']:
            playlists.append({'name': playlist['name'],
                              'owner': playlist['owner'],
                              'id': playlist['id']})

    return playlists


def choose_dest_playlist(spot_conn):
    """

    Choose playlist to add the songs into

    """
    playlists = get_user_playlists(spot_conn)

    choices = list(map(lambda playlist: (playlist['name'], ""), playlists))

    text = """Where should those %d songs be added to?""" % (len(ALL_SONGS))

    code, tag = DIALOG.menu(text, choices=choices)
    if code == DIALOG.OK:
        return [x for x in playlists if x['name'] == tag][0]['id']
    return False


def choose_playlists(spot_conn):
    """

    Choose playlists from all user playlists

    """
    playlists = get_user_playlists(spot_conn)

    choices = list(map(lambda playlist: (playlist['name'], "", False), playlists))

    code, tags = DIALOG.checklist(text="Which playlists would you like to search for artists?",
                                  choices=choices)
    if code == DIALOG.OK:
        if len(tags) < 1:
            return False
        return [x for x in playlists if x['name'] in tags]
    return False


def check_artist_top_songs(spot_conn, artist_id):
    """

    Get Top 10 songs of artist, add them to the frey

    """

    country = conf.get_key('Other', 'country')
    top_tracks = spot_conn.artist_top_tracks(artist_id, country=country if country else "US")

    num_tracks = 0
    track_names = []
    track_uris = []
    tracks = top_tracks['tracks']
    for track in tracks:
        track_name = track['name']
        track_names.append(track_name)
        track_uris.append(track['uri'])
        ALL_SONGS.add(track['uri'])
        num_tracks += 1
    num_tracks -= delete_duplicate_songs(track_names, track_uris)
    return num_tracks


def get_artists_from_list(spot_conn, list_name):
    """

    Get all artists from list

    """
    i = 0
    DIALOG.gauge_start(text="Gathering artists", percent=0)
    this_list, length = fi.get_list(list_name)
    #artist[0] == name; artist[1] == id
    for artist in this_list:
        DIALOG.gauge_update(math.floor((i/length)*100))
        if isinstance(artist, list):
            if len(artist) == 1:
                artist_id = check_and_get_artist_id(spot_conn, artist[0])
                fi.add_missing_id(list_name, artist[0], artist_id, artist)
                artist.append(artist_id)
        elif isinstance(artist, str):
            artist_id = check_and_get_artist_id(spot_conn, artist)
            fi.add_missing_id(list_name, artist, artist_id, [artist])
            artist = [artist].append(artist_id)
        else:
            raise TypeError("Artist entry is neither list nor string type")
        ARTISTS_DICT[artist[0]] = artist[1]
        ARTISTS_SET.add(artist[1])
        i += 1
    DIALOG.gauge_stop()

def get_artists_from_followed(spot_conn):
    """

    Get all artists that you are following

    """
    artists_page = spot_conn.current_user_followed_artists(limit=10)

    total_artists = artists_page['artists']['total']
    clear_screen()
    DIALOG.gauge_start(text="Gathering artists", percent=0)

    for artist in artists_page['artists']['items']:
        ARTISTS_SET.add(artist['id'])
        ARTISTS_DICT[artist['name']] = artist['id']

    i = len(artists_page['artists']['items'])
    while artists_page['artists']['next']:
        DIALOG.gauge_update(round((i/total_artists)*100))
        artists_page = spot_conn.next(artists_page['artists'])
        for artist in artists_page['artists']['items']:
            ARTISTS_DICT[artist['name']] = artist['id']
            ARTISTS_SET.add(artist['id'])
        i += len(artists_page['artists']['items'])


    _ = fi.remove_blocklisted(ARTISTS_DICT, ARTISTS_SET)
    DIALOG.gauge_stop()
    return True


def get_artists_from_playlist(spot_conn):
    """

    Get all artists from specific playlist

    """
    playlists = choose_playlists(spot_conn)
    if not playlists:
        return False

    # Get set of all needed artist id's
    fst_artist = True
    #for playlist in playlists['items']:
    i = 0
    DIALOG.gauge_start(text="Gathering artists", percent=0)
    for playlist in playlists:
        DIALOG.gauge_update(round((i/len(playlists))*100))
        i += 1

        playlist_tracks = []
        track_page = spot_conn.playlist_tracks(playlist['id'],
                                               limit=100)
        playlist_tracks.extend(track_page['items'])
        while track_page['next']:
            track_page = spot_conn.next(track_page)
            playlist_tracks.extend(track_page['items'])
        for track in playlist_tracks:
            fst_artist = True
            if not track['is_local']:
                for artist in track['track']['artists']:
                    if fst_artist:
                        ARTISTS_SET.add(artist['id'])
                        ARTISTS_DICT[artist['name']] = artist['id']
                        fst_artist = False

    _ = fi.remove_blocklisted(ARTISTS_DICT, ARTISTS_SET)
    DIALOG.gauge_stop()
    return True


def get_top_songs(spot_conn):
    """

    Get top songs from artists

    """
    inv_artists_dict = {v: k for k, v in ARTISTS_DICT.items()}
    i = 0
    DIALOG.gauge_start(text="Finding tracks", percent=0)
    for artist_id in ARTISTS_SET:
        artist_name = inv_artists_dict[artist_id]
        DIALOG.gauge_update(text="Getting top tracks by %s" % (artist_name),
                            percent=round((i/len(ARTISTS_SET))*100), update_text=True)
        i += 1
        check_artist_top_songs(spot_conn, artist_id)

    DIALOG.gauge_stop()


def get_new_songs(spot_conn):
    """

    Get new songs

    """
    standard_choices = [("A", "Only add to new songs"),
                        ("W", "Add new songs and add artist to allowlist"),
                        ("I", "Ignore new songs of this artist"),
                        ("B", "Add artist to blocklist and ignore songs"),
                        ("AA", "Add ALL new songs of new artists"),
                        ("WA", "Add ALL new songs and send ALL new artists to allowlist"),
                        ("IA", "Ignore ALL new songs from new artists"),
                        ("BA", "Ignore ALL new songs and send ALL new artists to blocklist")]
    inv_artists_dict = {v: k for k, v in ARTISTS_DICT.items()}
    i = 1
    skip_all = False
    DIALOG.gauge_start(text="Finding tracks", percent=0)
    for artist_id in ARTISTS_SET:
        artist_name = inv_artists_dict[artist_id]
        artist_info = [artist_name, artist_id]
        DIALOG.gauge_update(text="Finding tracks by %s" % (artist_name),
                            percent=math.floor((i/len(ARTISTS_SET))*100), update_text=True)
        i += 1
        new_artist = False
        if not fi.check_if_on_list(fi.Lists.ALLOWLIST, artist_info):
            new_artist = True
            # Oh nice, a new one
            if fi.check_if_on_list(fi.Lists.GREYLIST, artist_info):
                continue # Just ignore Greylist ones
                #text = """This one is already on your greylist! \
                #          What should happen to %s?""" % (artist_name)
                #choices = [("T", "Ignore new songs here, only add Top 10 songs")] + \
                #          standard_choices + \
                #          [("TA", "Ignore all new Greylist songs here, \
                #                  add Top 10 songs of all Greylist entries")]
            fi.add_to_list(fi.Lists.GREYLIST, artist_info)
            fi.sort_list(fi.Lists.GREYLIST)
            if not skip_all:
                text = """This is a new one! Added to greylist. \
                          What should happen to %s?""" % (artist_name)
                choices = standard_choices

                #DIALOG.clear()
                code, tag = DIALOG.menu(text, width=0, choices=choices, no_tags=True)
                if code != DIALOG.OK:
                    return False
                if tag in ("AA", "WA", "IA", "BA"):
                    skip_all = True
                DIALOG.gauge_start(text="Finding tracks by %s" % (artist_name),
                                   percent=round((i/len(ARTISTS_SET))*100))
            else:
                continue

        if not new_artist or tag in ("A", "AA"):
            check_artist_albums(spot_conn, artist_info)
        elif tag in ("W", "WA"):
            fi.add_to_list(fi.Lists.ALLOWLIST, artist_info)
            fi.sort_list(fi.Lists.ALLOWLIST)
            check_artist_albums(spot_conn, artist_info)
        elif tag in ("B", "BA"):
            fi.add_to_list(fi.Lists.BLOCKLIST, artist_info)
            fi.sort_list(fi.Lists.BLOCKLIST)
        elif tag in ("I", "IA"):
            pass
        else:
            pass

    DIALOG.gauge_stop()
    return True

def get_songs(spot_conn, state):
    """

    Fetch songs from any source

    """
    source = conf.get_key('Other', 'source')
    if state == States.TOP_10_GREY:
        get_artists_from_list(spot_conn, fi.Lists.GREYLIST)
        get_top_songs(spot_conn)
    elif state == States.NEW_RELEASES:
        if source == 'allowlist':
            get_artists_from_list(spot_conn, fi.Lists.ALLOWLIST)
        elif source == 'saved':
            get_artists_from_followed(spot_conn)
        else: # Playlist(s)
            if not get_artists_from_playlist(spot_conn):
                state = States.START
                return False, state

        if not get_new_songs(spot_conn):
            state = States.START
            return False, state
    else:
        # Wrong state
        DIALOG.msgbox("You ended up in a wrong state, back to the menu")
        return False, None
    return True, None

def add_songs_to_playlist(spot_conn):
    """

    Add new songs to specific playlist

    """
    song_list = []
    text = """ Do you wanna add all those %d songs?""" % (len(ALL_SONGS))

    if DIALOG.yesno(text) == DIALOG.OK:
        dest_playlist = choose_dest_playlist(spot_conn)
        for song in ALL_SONGS:
            song_list.append(song)
        chunked_list = [song_list[i:i + 10] for i in range(0, len(song_list), 10)]
        i = 0
        DIALOG.gauge_start(text="Add songs to playlist", percent=0)
        for chunk in chunked_list:
            DIALOG.gauge_update(percent=round((i/len(chunked_list))*100))
            i += 1
            spot_conn.user_playlist_add_tracks(conf.get_key('Auth', 'username'),
                                               dest_playlist, chunk)

        DIALOG.gauge_stop()
    else:
        return False
    return True

def clear_screen():
    """ Clear screen to avoid merging of output """
    # This program comes with ncurses
    program = "clear"

    process_clear = subprocess.Popen([program], shell=False, stdout=None,
                                     stderr=None, close_fds=True)
    _ = process_clear.wait()

if __name__ == '__main__':
    main()
