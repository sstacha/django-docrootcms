"""
Basic conversion utilities
"""
import json
import re
import pytz
# import requests
import xml.etree.ElementTree as Etree

from typing import List
from datetime import datetime
from collections import defaultdict
from collections import namedtuple
from django.conf import settings
# from django.utils import timezone
from django.db.models.fields.related import ManyToManyField

from .settings import TRUE_VALUES
from .settings import FALSE_VALUES
from .settings import to_bool as settings_to_bool

# TRUE_VALUES = ["1", 1, "y", "Y", True, "t", "T", "TRUE", "True", "true", "YES", "Yes", "yes", "ON", "On", "on"]
# FALSE_VALUES = ["0", 0, "n", "N", False, "f", "F", "False", "false", "No", "no", None]
DEFAULT_TIMEZONE = getattr(settings, "TIME_ZONE", pytz.timezone('UTC'))
DEFAULT_NAIVE = not getattr(settings, "USE_TZ", True)


# -------- date conversions --------
def to_iso8601(value=None, tz=DEFAULT_TIMEZONE):
    if not value:
        value = datetime.now(tz)
    if not value.tzinfo:
        value = tz.localize(value)
    _value = value.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    return _value[:-8] + _value[-5:]  # Remove microseconds


def to_aware(value=None, tz=DEFAULT_TIMEZONE):
    # don't allow overriding tz to None
    if tz is None:
        tz = DEFAULT_TIMEZONE
    if isinstance(value, datetime) and not value.tzinfo:
        if isinstance(tz, str):
            tz = pytz.timezone(tz)
        return tz.localize(value)
    return value


def from_iso8601(value=None, tz=DEFAULT_TIMEZONE, naive=DEFAULT_NAIVE):
    _value = value
    if isinstance(value, str):
        if len(value.strip()) == 0:
            return None
        # remove colons and dashes EXCEPT for the dash indicating + or - utc offset for the timezone
        conformed_timestamp = re.sub(r"[:]|([-](?!((\d{2}[:]\d{2})|(\d{4}))$))", "", value)
        _value = None
        try:
            _value = datetime.strptime(conformed_timestamp, "%Y%m%dT%H%M%S.%f%z")
        except ValueError:
            try:
                _value = datetime.strptime(conformed_timestamp, "%Y%m%dT%H%M%S.%f")
            except ValueError:
                try:
                    _value = datetime.strptime(conformed_timestamp, "%Y%m%dT%H%M%S")
                except ValueError:
                    try:
                        _value = datetime.strptime(conformed_timestamp, "%Y%m%dT%H%M")
                    except ValueError:
                        try:
                            _value = datetime.strptime(conformed_timestamp, "%Y%m%dT%H")
                        except ValueError:
                            try:
                                _value = datetime.strptime(conformed_timestamp, "%Y%m%d")
                            except ValueError:
                                raise ValueError(f"DateTime string [{value}] did not match an expected pattern.")
    if not naive:
        _value = to_aware(_value, tz)
    return _value


def from_db(value=None, tz=DEFAULT_TIMEZONE, naive=DEFAULT_NAIVE):
    """
    convert from database format to date if possible; Note we test exact format to prevent false positives
    @param value: value to convert
    @param tz: overridden timezone info
    @param naive: boolean if we specifically want naive date back (defaults to what settings has)
    @return: date or ValueError or None
    """
    _value = value
    if isinstance(value, str):
        if len(value.strip()) == 0:
            return None
        try:
            _value = datetime.strptime(value, "%Y-%m-%d %H%M%S.%f%z")
        except ValueError:
            try:
                _value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                try:
                    _value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        _value = datetime.strptime(value, "%Y-%m-%d %H:%M")
                    except ValueError:
                        try:
                            _value = datetime.strptime(value, "%Y-%m-%d %H")
                        except ValueError:
                            try:
                                _value = datetime.strptime(value, "%Y-%m-%d")
                            except ValueError:
                                raise ValueError(f"DateTime string [{value}] did not match an expected pattern.")
    if not naive:
        _value = to_aware(_value, tz)
    return _value


def to_date(value=None, tz=DEFAULT_TIMEZONE, none_to_now=True, naive=DEFAULT_NAIVE):
    """
    Convert string to python date.  Currently, only concerned about iso8601 and db type formats.
    None returns current date by default but can be overridden with none_to_now optional parameter
    :param value: string value for date (currently only iso8601)
    :param tz: pytz timezone (defaults to setting DEFAULT_TIMEZONE or 'America/Chicago')
    :param none_to_now: override the default to return now if none is passed; primarily for db operations to store null
    :param naive: should we return a naive datetime instead of converting even if USE_TZ is set
    :return: python date or None
    """
    if value is None and none_to_now:
        if naive:
            return datetime.now()
        # if we don't have a valid timezone try to convert
        if isinstance(tz, str):
            tz = pytz.timezone(tz)
        return datetime.now(tz)
    try:
        value = from_db(value, tz, naive)
    except ValueError:
        value = from_iso8601(value, tz, naive)
    if not isinstance(value, datetime):
        return None
    return value


# -------- primitive conversions --------
def to_int(value, default=0, none_to_default=True):
    """
    Convert <value> to int.  Will always return integer or none instead of throwing exception
    @param value: value to be converted
    @param default: default value to use if none or error (defaults to 0 but set to None to have nulls in db)
    @param none_to_default: preserve a None value or convert to the default; Note: still checks default value afterwards
    @return: integer value or default or None depending on options
    """
    if value is None and not none_to_default:
        return None
    if value is None:
        value = default
    try:
        return int(value)
    except Exception:
        # if any exception occurs lets print to screen and then return the supplied default value
        print(f"WARNING: exception converting <{str(value)}> to int; returning default value: {str(default)}!")
        return default


def to_bool(value):
    return settings_to_bool(value)


def to_none(value, values_to_convert: List[str] = ('None', '')):
    """
    Convert a string value to python None if it matches values_to_convert list of strings
    NOTE: this is helpful for converting string parameter values to None for storage in databases
    NOTE: we will strip the value first during comparison but not the value returned
    :param value: value to be converted
    :param values_to_convert: values to convert if matched
    :return: None if stripped string matches string in list otherwise the original value
    """
    if isinstance(value, str):
        if value.strip() in values_to_convert:
            return None
    return value


def to_js_bool(bool_value):
    """
    Convert python True/False to javascript string "true"/"false" for easily adding parameter to top of page scripts
    so javascript code can use.  Handy for placing context values from context into javascript variables on a page
    :param bool_value: expects python True/False value or None
    :return: Javascript string value "true"/"false"
    """
    if bool_value is True:
        return "true"
    return "false"


def to_true_value(value):
    """
    Convert <value> to a True boolean value.  Useful when you want to convert a passed parameter to True if it matches
    one of the defined TRUE_VALUES above; otherwise False.
    NOTE: unlike to_bool does not use Truthy value so any value not defined in list is considered False period.
    EX: "somestring" = False instead of Truthy True value
    :param value: expects int, bool, string or None
    :return: python True/False value
    """
    if value is not None:
        if value in TRUE_VALUES:
            return True
    return False


def dict_from_object(instance):
    """
    Convert an object to a dictionary set of values.  Preserves editable fields and many to many fields on models.
    NOTE: this uses a _meta field and therefore may break in the future.  Primarily using it to save space for
    cached data or debug print values for a model easily.
    :param instance: a class instance
    :return: a dictionary of
    """
    opts = instance._meta
    data = {}
    for f in opts.concrete_fields + opts.many_to_many:
        if isinstance(f, ManyToManyField):
            if instance.pk is None:
                data[f.name] = []
            else:
                data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))
        else:
            data[f.name] = f.value_from_object(instance)
    return data


# -------- cursor conversions --------
def values_from_cursor(cursor):
    """
    Convert a single value set of results to a list of element values
    :param cursor: database results cursor
    :return: list of values
    """
    return [
        row[0] for row in cursor.fetchall()
    ]


def dict_from_cursor(cursor):
    """
    Convert all rows from a cursor of results as a list of dicts
    :param cursor: database results cursor
    :return: list of dicts containing field_name:value
    """
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def tuple_from_cursor(cursor):
    """
    Convert all rows from a cursor of results as a list of tuples
    :param cursor: database results cursor
    :return: list of values
    """
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


# # -------- web services conversions --------
# def text_from_ws(ws_url, headers_dict=None):  # todo: consider adding params_dict
#     """
#     Read data from a web service url endpoint and return as text
#     :param ws_url: webservice endpoint URL
#     :param headers_dict: dictionary of headers to add to the request
#     :return: the data as a string or an Exception
#
#     example headers dict:
#     {'accept': 'application/json', 'authorization': settings.SPE_EVENT_SCHEDULES_OASIS_AUTH_HEADER_VALUE}
#
#     todo: consider extending to add params if passed
#     params = {'id': code, 'status': 'active'}
#     r = requests.get(url, params=params)
#     """
#     r = requests.get(ws_url, headers=headers_dict)
#     if r.status_code == 200:
#         return r.text
#     elif r.status_code == 204:
#         return ''
#     else:
#         print('')
#         print('----------')
#         print("error retrieving information from webservice:")
#         print(r.url)
#         print(strip_tags(r.text))
#         print('----------')
#         print('')
#         if r.status_code >= 400:
#             raise Exception("[" + str(r.status_code) + "] " + str(r.text) + ": " + str(r.url))
#         return r.text


def dict_from_etree(t):
    """
    Convert an etree structure to a dictionary of values
    :param t: etree instance
    :return: dictionary of values
    """
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(dict_from_etree, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v)
                        for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def dict_from_json_file(json_file_path):
    """
    Read and convert a json file to a dictionary of values
    :param json_file_path: path or string of file
    :return: json data
    """
    with open(json_file_path, encoding='utf-8-sig') as json_file:
        text = json_file.read()
        json_data = json.loads(text)
        return json_data


def dict_from_xml_file(xml_file_path, fix_ampersands=False):
    """
    Read and convert an xml file to a dictionary of values
    :param xml_file_path: path or string of file
    :param fix_ampersands: additionally replace & to &amp; encoded value before parsing to etree
    :return: dictionary of data
    """
    if fix_ampersands:
        with open(xml_file_path, encoding='utf-8-sig') as xml_file:
            text = xml_file.read()
            fixed_text = re.sub(r'&', '&amp;', text)
            root = Etree.fromstring(fixed_text)
    else:
        tree = Etree.parse(xml_file_path)
        root = tree.getroot()
    data_dict = dict_from_etree(root)
    return data_dict


def dict_from_xml_text(xml_text, fix_ampersands=False):
    """
    Convert an xml string to a dictionary of values
    :param xml_text: valid xml string
    :param fix_ampersands: additionally replace & to &amp; encoded value before parsing to etree
    :return: dictionary of data
    """
    if fix_ampersands:
        xml_text = re.sub(r'&', '&amp;', xml_text)
    root = Etree.fromstring(xml_text)
    return dict_from_etree(root)


def dict_from_json_text(json_text, fix_ampersands=False):
    """
    Convert a json string to a dictionary of values
    :param json_text: valid json string
    :param fix_ampersands: additionally replace & to &amp; encoded value before parsing
    :return: dictionary of data
    """
    if fix_ampersands:
        json_text = re.sub(r'&', '&amp;', json_text)
    return json.loads(json_text)
