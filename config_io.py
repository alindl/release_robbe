"""

Simple interface to read from the config file

Author: Andreas Lindlbauer (@alindl)

"""

import configparser
import re
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
    set_key('Other', 'last_check', str(datetime.now().timestamp()))

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

def get_credentials():
    """

    Get credentials and check if they are filled

    """
    information = [get_key('Auth', 'username'),
                   get_key('Auth', 'client_id'),
                   get_key('Auth', 'client_secret'),
                   get_key('Other', 'country'),
                   get_key('Lists', 'allowlist'),
                   get_key('Lists', 'greylist'),
                   get_key('Lists', 'blocklist')
                   ]
    empty = False
    for date in information:
        if not date:
            empty = True
    if empty: # Some are empty
        return False, information
    # All entries have information

    return True, information

def check_credentials(information):
    """

    Check if credentials are valid

    """
    re_client = "^[a-z0-9]{32}$"
    re_iso_3166_1_alpha_2 = re.compile(r"^(AF|AX|AL|DZ|AS|AD|AO|AI|AQ|AG|AR|AM|AW|AU|AT|AZ|BS|BH|BD"
    r"|BB|BY|BE|BZ|BJ|BM|BT|BO|BQ|BA|BW|BV|BR|IO|BN|BG|BF|BI|KH|CM|CA|CV|KY|CF|TD|CL|CN|CX|CC|CO"
    r"|KM|CG|CD|CK|CR|CI|HR|CU|CW|CY|CZ|DK|DJ|DM|DO|EC|EG|SV|GQ|ER|EE|ET|FK|FO|FJ|FI|FR|GF|PF|TF"
    r"|GA|GM|GE|DE|GH|GI|GR|GL|GD|GP|GU|GT|GG|GN|GW|GY|HT|HM|VA|HN|HK|HU|IS|IN|ID|IR|IQ|IE|IM|IL"
    r"|IT|JM|JP|JE|JO|KZ|KE|KI|KP|KR|KW|KG|LA|LV|LB|LS|LR|LY|LI|LT|LU|MO|MK|MG|MW|MY|MV|ML|MT|MH"
    r"|MQ|MR|MU|YT|MX|FM|MD|MC|MN|ME|MS|MA|MZ|MM|NA|NR|NP|NL|NC|NZ|NI|NE|NG|NU|NF|MP|NO|OM|PK|PW"
    r"|PS|PA|PG|PY|PE|PH|PN|PL|PT|PR|QA|RE|RO|RU|RW|BL|SH|KN|LC|MF|PM|VC|WS|SM|ST|SA|SN|RS|SC|SL"
    r"|SG|SX|SK|SI|SB|SO|ZA|GS|SS|ES|LK|SD|SR|SJ|SZ|SE|CH|SY|TW|TJ|TZ|TH|TL|TG|TK|TO|TT|TN|TR|TM"
    r"|TC|TV|UG|UA|AE|GB|US|UM|UY|UZ|VU|VE|VN|VG|VI|WF|EH|YE|ZM|ZW)$")
    re_file = re.compile(r"^\/?([A-z0-9-_+]+\/)*([A-z0-9]+\.(csv))$")

    error_msg = ""

    if not information[0]:
        error_msg += "\n· No Username"
    if not re.search(re_client, information[1]):
        error_msg += "\n· Not a valid Client ID"
    if not re.search(re_client, information[2]):
        error_msg += "\n· Not a valid Client Secret"
    if not re.search(re_iso_3166_1_alpha_2, information[3]):
        error_msg += "\n· Not a valid two-letter country code(ISO 3166-1 alpha-2)"
    if not re.search(re_file, information[4]):
        error_msg += "\n· Allowlist does not have a valid filename/path"
    if not re.search(re_file, information[5]):
        error_msg += "\n· Greylist does not have a valid filename/path"
    if not re.search(re_file, information[6]):
        error_msg += "\n· Blocklist does not have a valid filename/path"

    if error_msg:
        return False, error_msg

    return True, error_msg
