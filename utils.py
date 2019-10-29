# coding:utf-8

<<<<<<< HEAD
import time
import base64
from datetime import datetime, date, timedelta
from uuid import uuid4


def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")


def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_date_interval_between_iter(start_time, end_time):
    start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    diff_time = end_time - start_time
    interval_between = map(lambda x: timedelta(days=x) +
                           start_time, range(diff_time.days+1))
    return iter(interval_between)


def delta_tomorrow():
    current = int(time.time())
    tomorrow = date.today() + timedelta(days=1)
    tomorrow_time = int(time.mktime(tomorrow.timetuple()))
    return tomorrow_time - current


def get_current_seconds():
    return int(time.time())
=======
import base64
from datetime import datetime
from uuid import uuid4


def get_standard_datetime(time_string):
    timestamp = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
    return timestamp.strftime("%Y%m%d%H%M%S")


def get_standard_date(date_string):
    timestamp = datetime.strptime(date_string, "%Y-%m-%d")
    return timestamp.strftime("%Y%m%d")
>>>>>>> e9d55abc7291c3337afc428eadacb3bf86399625


def get_timestamp_from_iso_time(iso_time):
    timestamp = datetime.strptime(iso_time[:19], "%Y-%m-%dT%H:%M:%S")
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def encode_picture(raw_data):
    encoded_data = base64.b64encode(raw_data)
    return encoded_data.decode("utf-8")


<<<<<<< HEAD
=======
def decode_base64(raw_data):
    picture = base64.b64decode(raw_data)
    return picture


>>>>>>> e9d55abc7291c3337afc428eadacb3bf86399625
def get_unique_id():
    return uuid4().hex


<<<<<<< HEAD
def zip_dict(key, var):
    t = dict()
    if not key or not var:
        return t

    def time_format(x):
        if isinstance(x, datetime):
            return x.strftime("%Y-%m-%d %X")
        elif isinstance(x, date):
            return x.strftime("%Y-%m-%d")
        else:
            return x

    for i in range(len(key)):
        t[key[i]] = time_format(var[i])
    return t


def fix_estate_id(param_estate_id):
    """

    :param param_estate_id:
    :type param_estate_id: str
    :return:
    >>> fix_estate_id(7)
    '7'
    >>> fix_estate_id("7")
    '7'
    >>> fix_estate_id("001234567")
    '1234567'
    >>> fix_estate_id(891234567)
    '1234567'
    >>> fix_estate_id(897654321)
    '7654321'
    """
    if isinstance(param_estate_id, int):
        param_estate_id = str(param_estate_id)
    if len(param_estate_id) <= 7:
        estate_code = param_estate_id
    else:
        estate_code = param_estate_id[-7:]
    return int(estate_code)
=======
def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_date_and_time(time_string):
    timestamp = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
    return timestamp.strftime("%Y-%m-%d"), timestamp.strftime("%H:%M:%S")


def get_time_from_timestamp(time_string):
    timestamp = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
    return int(timestamp.timestamp())
>>>>>>> e9d55abc7291c3337afc428eadacb3bf86399625
