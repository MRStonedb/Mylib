# coding:utf-8

import base64
from datetime import datetime
from uuid import uuid4


def get_standard_datetime(time_string):
    timestamp = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
    return timestamp.strftime("%Y%m%d%H%M%S")


def get_standard_date(date_string):
    timestamp = datetime.strptime(date_string, "%Y-%m-%d")
    return timestamp.strftime("%Y%m%d")


def get_timestamp_from_iso_time(iso_time):
    timestamp = datetime.strptime(iso_time[:19], "%Y-%m-%dT%H:%M:%S")
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def encode_picture(raw_data):
    encoded_data = base64.b64encode(raw_data)
    return encoded_data.decode("utf-8")


def decode_base64(raw_data):
    picture = base64.b64decode(raw_data)
    return picture


def get_unique_id():
    return uuid4().hex


def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_date_and_time(time_string):
    timestamp = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
    return timestamp.strftime("%Y-%m-%d"), timestamp.strftime("%H:%M:%S")


def get_time_from_timestamp(time_string):
    timestamp = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S")
    return int(timestamp.timestamp())
