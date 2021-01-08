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


# def edit_list(list_name, text):
#     """
#
#     Edit whole list
#
#     """
#     # I'm trusting that nobody would use the wrong delimiter
#     # I could make a form with all entries to solve that
#     with open(list_name.value, 'w') as this_list:
#         this_list.write(text)


def add_to_list(list_name, artist):
    """

    Write artist to list file

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
                # We could also add the id here
                this_list.write(artist[0] + '\n')
            else:
                raise ValueError("Should be [artistname, id] or [artist]")
            # FIXME What if it is a string?
            return True
    return False


def get_length_of_list(list_name):
    """

    Get length of the list == number of artists

    """
    with open(list_name.value) as this_list:
        return sum(1 for line in this_list)


def get_list(list_name):
    """

    Get all artists + id from list as list and length

    """
    #all_artists = []
    with open(list_name.value, 'r') as this_list:
        csv_reader = csv.reader(this_list, delimiter=';')
        all_artists = list(csv_reader)
        return all_artists, len(all_artists)
        #for row in csv_reader:
        #    i += 1
        #    all_artists.append(row)
    #return all_artists, i

def sort_list(list_name):
    """

    Sort a list

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
        #for line in sorted_list:
        #    this_list.write(line)

def fast_search(list_name, artist):
    d = {}

    f = open(list_name.value, "r")
    for line in f:
        line = line.rstrip()
        l = len(line)+1
        for i in range(1,l):
            d[line[:i]] = True
    f.close()


    while True:
        w = artist
        if not w:
            break

        if w in d:
            return w


def bin_search_on_list(list_name, artist):
    """

    Do binary search on a list

    """
    with open(list_name.value, 'r', encoding='utf-8') as this_list:
        low = 0
        this_list.seek(0, 2)
        high = this_list.tell()
        while low < high:
            mid = (low+high)//2
            pointer = mid
            while pointer >= 0:
                this_list.seek(pointer)
                #print(this_list.read())
                if this_list.read(1) == '\n':
                    break
                pointer -= 1
            if pointer < 0:
                this_list.seek(0)
            line = this_list.readline()
            if line.split(';')[0] < artist[0]:
                low = mid+1
            else:
                high = mid

        pointer = low
        while pointer >= 0:
            this_list.seek(pointer)
            if this_list.read(1) == '\n':
                break
            pointer -= 1
        if pointer < 0:
            this_list.seek(0)

        line = this_list.readline()
        if line[-1:] == '\n':
            line = line[:-1]
        if line.split(';')[0] == artist[0]:
            return line.split(';')
        return False


def bisect_right(rows, artist, lo=0, hi=None):
    if hi is None:
        hi = len(rows)
    while lo < hi:
        mid = (lo + hi) // 2
        if artist[0] < rows[mid][0]:
            hi = mid
        else:
            lo = mid + 1
    return lo

def bisect_left(rows, artist, lo=0, hi=None):
    if hi is None:
        hi = len(rows)
    while lo < hi:
        mid = (lo + hi) // 2
        if rows[mid][0].lower() < artist[0].lower():
            lo = mid + 1
        else:
            hi = mid
    return lo

def search_list(list_name, artist):
    whole_list, _ = get_list(list_name)
    idx = bisect_left(whole_list, artist)
    #print(len(whole_list), idx)
    if len(whole_list) <= idx or \
       (isinstance(artist, list) and whole_list[idx][0].lower() != artist[0].lower()) or \
       (isinstance(artist, str) and whole_list[idx][0].lower() != artist.lower()):
        #if len(whole_list) > idx:
        #    print(list_name.value, whole_list[idx], artist)
        return False
    return whole_list[idx]

def check_if_on_list(list_name, artist):
    """

    Check if artist is on this list

    """
    #entry = bin_search_on_list(list_name, artist)
    entry = search_list(list_name, artist)
    if entry: # Entry found
        if len(entry)+len(artist) == 4: # both have id
            if entry[1] != artist[1]: # names match, but ids don't -> id wrong
                add_missing_id(list_name, artist[0], artist[1], entry)
        elif len(artist) == 2: # input has id, entry in list doesn't -> put it in
            add_missing_id(list_name, artist[0], artist[1], entry)
        else: # either both have no id, or input has none. Nothing to do here
            pass
        #print("True", entry, artist)
        return entry
    #print("False", entry, artist)
    return False

    # with open(list_name.value, 'r') as this_list:
    #     csv_reader = csv.reader(this_list, delimiter=';')
    #     for row in csv_reader:
    #         if row[0] == artist[0]: # names match
    #             if len(row)+len(artist) == 4: # has id
    #                 if row[1] != artist[1]: # ids don't match, but names do -> id wrong
    #                     add_missing_id(list_name, artist[0], artist[1])
    #             else: # has no id
    #                 add_missing_id(list_name, artist[0], artist[1])
    #             return row
    # return False


def add_missing_id(list_name, artist_name, artist_id, entry):
    """

    Search list for artists that have no id

    """
    #entry = check_if_on_list(list_name, [artist_name, artist_id])
    #if not entry: # Artist not found
    #    return False
    if len(entry) == 2: # Already has id
        if re.search("^[0-9A-Za-z]{22}$", entry[1]) and entry[1] == artist_id:
            return True
        # ID is wrong! You almost got me in the first half
        entry = [entry[0]]
    if len(entry) == 1: # We know it's there but without an id
        read_csv = []
        with open(list_name.value, 'r') as this_list:
            read_csv = list(csv.reader(this_list, delimiter=';'))
        with open(list_name.value, 'w') as this_list:
            write_csv = csv.writer(this_list, delimiter=';')
            for line in read_csv:
                if line[0] == artist_name:
                    line.append(artist_id)
                write_csv.writerow(line)
        return True
    return False # Something went wrong


def delete_dupes_from_list(list_name):
    """

    Delete duplicates from list

    """
    read_csv = []
    deleted_dupes = 0
    with open(list_name.value, 'r') as this_list:
        read_csv = list(csv.reader(this_list, delimiter=';'))
    with open(list_name.value, 'w') as this_list:
        write_csv = csv.writer(this_list, delimiter=';')
        old_line = []
        for line in read_csv:
            if not old_line:
                write_csv.writerow(line)
                old_line = line
                continue
            if old_line == line:
                deleted_dupes += 1
                continue
            write_csv.writerow(line)
            old_line = line
    return deleted_dupes


def delete_from_list(list_name, artist):
    """

    Delete artist from list

    Parameters
    ----------
    list_name : Lists Enum
    artist : list item of name+id or str of name

    Returns
    -------
    `True` if entry was deleted, otherwise `False`.

    Examples
    --------
    >>> delete_from_list(Lists.ALLOWLIST, ['Billie Eilish', '6qqNVTkY8uBg9cP3Jd7DAH'])
    True
    >>> delete_from_list(Lists.ALLOWLIST, ['Billie Eilish', '6qqNVTkY8uBg9cP3Jd7DAH'])
    False
    >>> delete_from_list(Lists.ALLOWLIST, ['Bilderbuch'])
    True
    >>> delete_from_list(Lists.ALLOWLIST, 'Frittenbude')
    True
    >>> delete_from_list("Allowlist.csv", 'Gesaffelstein')
    False

    """
    # Parameter checking
    # TODO Should probably be it's own method
    if not isinstance(list_name,Lists):
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
        if isinstance(artist,str):
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
            # I have to write the whole file anyway I think, so no time lost
            # First check the id, then the name -> safer, less possibility of false positive
            # Gotta check the timing here, could be slower
            if ((artist_id != line[1]) if (artist_id and (len(line) == 2)) else True):
                if line[0] != artist_name:
                    write_csv.writerow(line)
                else:
                    deleted_value = True
            else:
                deleted_value = True
    return deleted_value


def move_artist_between_lists(list_from, list_to, artist):
    """

    Move artist from list A to list B

    Parameters
    ----------
    list_from : Lists Enum
    list_to : Lists Enum
    artist : list item of name+id or str of name

    Returns
    -------
    `True` if entry was deleted, otherwise `False`.

    Examples
    --------
    >>> move_artist_between_lists(Lists.ALLOWLIST,
                                  Lists.BLOCKLIST,
                                  ['Billie Eilish', '6qqNVTkY8uBg9cP3Jd7DAH'])
    True
    >>> move_artist_between_lists(Lists.ALLOWLIST,
                                  Lists.BLOCKLIST,
                                  ['Billie Eilish', '6qqNVTkY8uBg9cP3Jd7DAH'])
    False
    >>> move_artist_between_lists(Lists.ALLOWLIST, ['Bilderbuch'])
    True
    >>> delete_from_list(Lists.ALLOWLIST, 'Frittenbude')
    True
    >>> delete_from_list("Allowlist", 'Gesaffelstein')
    False

    """
    # Parameter checking
    if not isinstance(list_from,Lists) or not isinstance(list_to,Lists):
        return False
    if not isinstance(artist, list):
        if not isinstance(artist,str):
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

    """
    removed_artists = 0
    artists_to_remove =[]
    for artist in artist_dict:
        #entry = bin_search_on_list(Lists.BLOCKLIST, artist)
        #entry = search_list(Lists.BLOCKLIST, artist)
        entry = check_if_on_list(Lists.BLOCKLIST, [artist, artist_dict[artist]])
        if entry: # entry found
            #    # No id
            removed_artists += 1
            #print(artist)
            # entry is just ['ARTISTNAME']
            artist_set.discard(artist_dict[artist])
            artists_to_remove.append(artist)
    for artist in artists_to_remove:
        del artist_dict[artist]
    return artist_dict, artist_set, removed_artists
