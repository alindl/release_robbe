"""

All kinds of file interactions

Subtasks:
    - Manage blocklist, allowlist, greylist
    - Search on lists using binary search
    - Add missing ids
    - Manage reading and writing the timestamps
    - Get correct format for release date


Author: Andreas Lindlbauer (@alindl)

"""
from enum import Enum
import re
import csv
import config_io as conf

class Lists(Enum):
    """

    Enum to represent the different lists

    """
    BLOCKLIST = conf.get_key("Lists", "blocklist")
    ALLOWLIST = conf.get_key("Lists", "allowlist")
    GREYLIST = conf.get_key("Lists", "greylist")
    DELETE = "delete"


def add_to_list(list_name, artist):
    """

    Add artist to list file

    Parameters
    ----------
    list_name : Lists Enum
    artist : List [str(,str)]

    Returns
    -------
    `True` if it was added, `False` if not.
    If the target was `delete`, do nothing and return `True`.

    Examples
    --------
    >>> add_to_list(Lists.BLOCKLIST, ['ABBA','0LcJLqbBmaGUft1e9Mm8HV'])
    True
    """
    if list_name.value == "delete":
        return True
    with open(list_name.value, "a") as this_list:
        # Don't even vomit wrong ids in my clean list
        if isinstance(artist,list):
            if len(artist) == 2:
                if re.search("^[0-9A-Za-z]{22}$", artist[1]):
                    this_list.write(';'.join(artist) + '\n')
                else:
                    print("invalid ID")
            elif len(artist) == 1:
                # NOTE We could also add the id here
                # But as we get this data from Spotify, it must have an id
                this_list.write(artist[0] + '\n')
            else:
                raise ValueError("Should be [artistname, id] or [artist]")
            # NOTE What if it is a string?
            return True
    return False


def get_length_of_list(list_name):
    """
    Get length of the list == number of artists

    Parameters
    ----------
    list_name : Lists Enum

    Returns
    -------
    Length of list

    Examples
    --------
    >>> get_length_of_list(Lists.ALLOWLIST)
    42
    """
    with open(list_name.value) as this_list:
        return sum(1 for line in this_list)


def get_list(list_name):
    """

    Get all artists + id from list as list and length

    Parameters
    ----------
    list_name : Lists Enum

    Returns
    -------
    Sorted list of artist list entries as [str(,str)], them being name and id

    Examples
    --------
    >>> get_list(Lists.ALLOWLIST)
    ['ABBA','0LcJLqbBmaGUft1e9Mm8HV'], [.,.], ...]
    """
    with open(list_name.value, 'r') as this_list:
        csv_reader = csv.reader(this_list, delimiter=';')
        all_artists = list(csv_reader)
        return all_artists, len(all_artists)

def sort_list(list_name):
    """

    Sort a list.

    Parameters
    ----------
    list_name : Lists Enum
    """
    with open(list_name.value, 'r') as this_list:
        # Read list from file
        sorted_list = this_list.readlines()
        # Strip of newlines, split by ';'
        sorted_list = list(map(lambda x: x.rstrip().split(';'), sorted_list))
        # Sort by first attribute alone
        sorted_list = sorted(sorted_list, key=lambda x: x[0].casefold())
        # Join each entry again, add newline again
        sorted_list = list(map(lambda y: y+'\n',[';'.join(x) for x in sorted_list]))
    with open(list_name.value, 'w') as this_list:
        this_list.writelines(sorted_list)

def sort_all_lists(dialog):
    """

    Sort all 3 lists, show progress bar.

    Parameters
    ----------
    dialog : dialog.Dialog object

    """
    dialog.gauge_start(text="Sorting all lists", percent=0)

    sort_list(Lists.ALLOWLIST)
    dialog.gauge_update(round(1/3)*100)

    sort_list(Lists.BLOCKLIST)
    dialog.gauge_update(round(2/3)*100)

    sort_list(Lists.GREYLIST)
    dialog.gauge_update(round(3/3)*100)

    dialog.gauge_stop()


def bisect_left(rows, artist, low=0, high=None):
    """

    Binary search on rows to find, where artist should be.

    Parameters
    ----------
    rows : List
    artist : List [str(,str)]
    low : int
    high : int

    Returns
    -------
    Return possible entry position.

    Examples
    --------
    >>> bisect_left([['ABBA','0LcJLqbBmaGUft1e9Mm8HV'], [.,.], ...],
                    ['PSY', '2dd5mrQZvg6SmahdgVKDzh'])
    42
    """
    if high is None:
        high = len(rows)
    while low < high:
        mid = (low + high) // 2
        if rows[mid][0].lower() < artist[0].lower():
            low = mid + 1
        else:
            high = mid
    return low

def search_list(list_name, artist):
    """

    Search through list using binary search.

    Parameters
    ----------
    list_name : Lists Enum
    artist : List [str(,str)]

    Returns
    -------
    Return possible entry if found, `False` or not.

    Examples
    --------
    >>> check_if_on_list(Lists.BLOCKLIST, ['PSY', '2dd5mrQZvg6SmahdgVKDzh'])
    ['PSY', '2dd5mrQZvg6SmahdgVKDzh']
    >>> check_if_on_list(Lists.BLOCKLIST, 'PSY')
    ['PSY', '2dd5mrQZvg6SmahdgVKDzh']
    >>> search_list(Lists.ALLOWLIST, ['PSY', '2dd5mrQZvg6SmahdgVKDzh'])
    False
    """
    whole_list, _ = get_list(list_name)
    idx = bisect_left(whole_list, artist)
    if len(whole_list) <= idx or \
       (isinstance(artist, list) and whole_list[idx][0].lower() != artist[0].lower()) or \
       (isinstance(artist, str) and whole_list[idx][0].lower() != artist.lower()):
        return False
    return whole_list[idx]

def check_if_on_list(list_name, artist):
    """

    Check if artist is on this list

    Parameters
    ----------
    list_name : Lists Enum
    artist : List [str(,str)]

    Returns
    -------
    `True` if it is on the list, `False` if not.

    Examples
    --------
    >>> check_if_on_list(Lists.ALLOWLIST, ['PSY', '2dd5mrQZvg6SmahdgVKDzh'])
    False
    >>> check_if_on_list(Lists.BLOCKLIST, ['PSY', '2dd5mrQZvg6SmahdgVKDzh'])
    True
    >>> check_if_on_list(Lists.BLOCKLIST, 'PSY')
    False
    """
    if not isinstance(artist, list):
        return False
    entry = search_list(list_name, artist)
    if entry: # Entry found
        if len(entry)+len(artist) == 4: # both have id
            if entry[1] != artist[1]: # names match, but ids don't -> id wrong
                add_missing_id(list_name, artist, entry)
        elif len(artist) == 2: # input has id, entry in list doesn't -> put it in
            add_missing_id(list_name, artist, entry)
        else: # either both have no id, or input has none. Nothing to do here
            pass
        return entry
    return False

def add_missing_id(list_name, artist, entry):
    """

    Search list for artists that have no id

    Parameters
    ----------
    list_name : Lists Enum
    artist : List [str,str] (known to be true)
    entry : List [str(,str)] (known to be on this list)

    Returns
    -------
    `True` if id was already good or has been added or fixed, `False` if neither.

    Examples
    --------
    >>> add_missing_id(Lists.ALLOWLIST, ['PSY', '2dd5mrQZvg6SmahdgVKDzh'], ['PSY'])
    True
    >>> add_missing_id(Lists.ALLOWLIST, ['PSY', '2dd5mrQZvg6SmahdgVKDzh'],
                                        ['PSY', '2dd5mrQZvg6SmahdgVKDzh'])
    True
    >>> add_missing_id(Lists.ALLOWLIST, ['PSY', '2dd5mrQZvg6SmahdgVKDzh'],
                                        ['PSY', 'aaaaaaaaaaaaaaaaaaaaaa'])
    True
    """
    # NOTE What if there are two artists, with the same name but different ids?
    if not (isinstance(entry, list) and isinstance(artist, list)):
        return False
    if len(entry) == 2: # Already has id
        if re.search("^[0-9A-Za-z]{22}$", entry[1]) and entry[1] == artist[1]:
            return True
        # ID is wrong! You almost got me in the first half
        entry = [entry[0]]
    if len(entry) == 1: # We know it's there but without an id
        read_csv = []
        with open(list_name.value, 'r') as this_list:
            read_csv = list(csv.reader(this_list, delimiter=';'))
        with open(list_name.value, 'w') as this_list:
            write_csv = csv.writer(this_list, delimiter=';')
            fixed = False
            for line in read_csv:
                if not fixed:
                    if line[0] == artist[0]:
                        line = artist
                        fixed = True
                write_csv.writerow(line)
        return fixed
    return False # Something went wrong

def delete_dupes_from_list(list_name):
    """

    Delete duplicates from list

    Parameters
    ----------
    list_name : Lists Enum

    Returns
    -------
    int of the number of duplicates that were removed

    """
    # NOTE What if the same entry exists with and without an id?
    read_csv = []
    deleted_dupes = 0
    with open(list_name.value, 'r') as read_list:
        read_csv = list(csv.reader(read_list, delimiter=';'))
    with open(list_name.value, 'w') as write_list:
        write_csv = csv.writer(write_list, delimiter=';')
        seen = set()
        for line in read_csv:
            if line in seen:
                deleted_dupes += 1
            else:
                seen.add(line)
                write_csv.writerow(line)
    return deleted_dupes

def compare_artists(line_in_csv, artist, write_csv):
    """

    Compare artist to line in csv file

    Parameters
    ----------
    line_in_csv : List [str(, str)]
    artist : List [str(,str)] or str
    write_csv : _csv.writer object

    Returns
    -------
    `True` if entry was deleted, `False` if not, else `IndexError`.

    Examples
    --------
    >>> compare_artists(['PSY', '2dd5mrQZvg6SmahdgVKDzh'], ['PSY', '2dd5mrQZvg6SmahdgVKDzh'], csv)
    True
    >>> compare_artists(['PSY', '2dd5mrQZvg6SmahdgVKDzh'], ['PSY'], csv)
    True
    >>> compare_artists(['PSY', '2dd5mrQZvg6SmahdgVKDzh'], 'PSY', csv)
    True
    >>> compare_artists(['PSY'], ['PSY'], csv)
    True
    >>> compare_artists(['PSY'], ['PSY', '2dd5mrQZvg6SmahdgVKDzh'], csv)
    True
    >>> compare_artists(['PSY', '2dd5mrQZvg6SmahdgVKDzh'], '2dd5mrQZvg6SmahdgVKDzh', csv)
    False
    >>> compare_artists(['PSY', '2dd5mrQZvg6SmahdgVKDzh'],
                        ['PSY', '2dd5mrQZvg6SmahdgVKDzh', 1], csv)
    IndexError("Expected 2 or 1 arguments [name(,id)]")
    """
    len_line = len(line_in_csv)
    # If there is not id in search
    if artist[1] is None or len_line == 1:
        # If the name matches
        if artist[0] == line_in_csv[0]:
            return True
        write_csv.writerow(line_in_csv)
        return False
    # If there is an id
    # If the entry in the list also has an id
    if len_line == 2:
        # If the id matches
        if artist[1] == line_in_csv[1]:
            return True
        write_csv.writerow(line_in_csv)
        return False
    raise IndexError("Expected 2 or 1 arguments [name(,id)]")
    # NOTE Gotta check the runtime here
    # Could be improved by re-write in a new file and move
    # Function call overhead is there, but negligible


def delete_from_list(list_name, artist):
    """

    Delete artist from list

    Parameters
    ----------
    list_name : Lists Enum
    artist : List [str(,str)] or str

    Returns
    -------
    `True` if entry was deleted, otherwise `False`.

    Examples
    --------
    >>> delete_from_list(Lists.ALLOWLIST, ['PSY', '2dd5mrQZvg6SmahdgVKDzh'])
    True
    >>> delete_from_list(Lists.ALLOWLIST, ['PSY', '2dd5mrQZvg6SmahdgVKDzh'])
    False
    >>> delete_from_list(Lists.ALLOWLIST, ['Bilderbuch'])
    True
    >>> delete_from_list(Lists.ALLOWLIST, 'Frittenbude')
    True
    """

    # Parameter checking
    # NOTE Should probably be it's own method
    if not isinstance(list_name, Lists):
        return False
    if isinstance(artist, list):
        if len(artist) == 2:
            # ['name','id']
            artist_name, artist_id = (artist[0], artist[1])
        elif len(artist) == 1:
            # ['name']
            artist_name, artist_id = (artist[0], None)
        else:
            # Empty list, or list is too long
            return False
    else:
        if isinstance(artist, str):
            # 'name' (Shouldn't even be possible)
            artist_name, artist_id = (artist, None)
        else:
            return False

    read_csv = []
    deleted_value = False
    with open(list_name.value, 'r') as this_list:
        read_csv = list(csv.reader(this_list, delimiter=';'))
    with open(list_name.value, 'w') as this_list:
        write_csv = csv.writer(this_list, delimiter=';')
        for line in read_csv:
            compare_artists(line, (artist_name, artist_id), write_csv)
    return deleted_value

def move_artist_between_lists(list_from, list_to, artist):
    """

    Move artist from list A to list B

    Parameters
    ----------
    list_from : Lists Enum
    list_to : Lists Enum
    artist : List [str(,str)] or str

    Returns
    -------
    `True` if entry was deleted, otherwise `False`.

    Examples
    --------
    >>> move_artist_between_lists(Lists.ALLOWLIST,
                                  Lists.BLOCKLIST,
                                  ['PSY', '2dd5mrQZvg6SmahdgVKDzh'])
    True
    >>> move_artist_between_lists(Lists.ALLOWLIST,
                                  Lists.BLOCKLIST,
                                  ['PSY', '2dd5mrQZvg6SmahdgVKDzh'])
    False
    >>> move_artist_between_lists(Lists.GREYLIST,
                                  Lists.ALLOWLIST,
                                  ['Bilderbuch'])
    True
    """
    # Parameter checking
    if not isinstance(list_from, Lists) or not isinstance(list_to, Lists):
        return False

    if not isinstance(artist, list):
        if not isinstance(artist, str):
            return False
    else:
        # Artist is list
        if 0 >= len(artist) > 2:
            return False

    if add_to_list(list_to, artist):
        if list_to != Lists.DELETE:
            sort_list(list_to)
        return delete_from_list(list_from, artist)
    print('not added')
    return False


def remove_blocklisted(artist_dict, artist_set):
    """

    Remove blocklisted artists

    Parameters
    ----------
    artist_dict : dict
    artist_set : set

    Returns
    -------
    Trimmed artists_dict, artists_set and the number of removed artists

    """
    artists_to_remove =[]
    for artist in artist_dict:
        #entry = search_list(Lists.BLOCKLIST, artist)
        entry = check_if_on_list(Lists.BLOCKLIST, [artist, artist_dict[artist]])
        if entry: # entry found
            #    # No id
            artists_to_remove.append(artist)
    for artist in artists_to_remove:
        artist_set.discard(artist_dict[artist])
        del artist_dict[artist]
    return artist_dict, artist_set, len(artists_to_remove)
