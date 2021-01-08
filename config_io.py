"""

Simple interface to read from the config file

Author: Andreas Lindlbauer (@alindl)

"""

import configparser
from datetime import datetime

def get_config():
    """

    Load config file

    """
    config = configparser.ConfigParser()
    config.read("release_robbe.conf")
    return config

def get_key(section, key):
    """

    Get key from config file

    """
    return get_config().get(section, key)

def set_key(section, key, value):
    """

    Set key from config file

    """
    config = get_config()
    config[section][key] = value
    with open('release_robbe.conf', 'w') as configfile:
        config.write(configfile)

def get_section(section):
    """

    Get section from config file

    """
    return get_config().items(section)

def convert_dt_to_iso(timestamp):
    """

    Convert datetime object to ISO format (YYY-MM-DD)

    """
    return timestamp.strftime("%Y-%m-%d")

def convert_list_to_ts(date_list):
    """

    Convert list of date ([DD, MM, YYYY]) to timestamp

    """
    return datetime(date_list[2], date_list[1], date_list[0]).timestamp()

def convert_iso_to_ts(date_string):
    """

    Convert ISO format (YYY-MM-DD) to timestamp

    """
    return datetime.strptime(date_string, "%Y-%m-%d").timestamp()

def read_time():
    """

    Read last time, this program was used, so we don't get duplicates

    """
    last_check = get_key('Other', 'last_check')
    if last_check:
        return datetime.fromtimestamp(float(last_check))
    return datetime.today().date()
    #return datetime(2019, 8, 3)
    # If there's no date, just use the date one year ago
    #last_check = datetime.today().date()
    #try:
    #    last_check = last_check.replace(year=last_check.year-1)
    #except ValueError:
    #    last_check = last_check.replace(year=last_check.year-1, day=last_check.day-1)
    #return last_check


def write_time():
    """

    Write time of usage

    """
    set_key('Auth', 'last_check', str(datetime.now().timestamp()))

def get_release_date(album):
    """

    Get release date according to precision

    """
    out_format = '%Y'
    if album['release_date_precision'] == 'day':
        out_format += '-%m-%d'
    elif album['release_date_precision'] == 'month':
        out_format += '-%m'
    else:
        pass
    return datetime.strptime(album['release_date'], out_format)
