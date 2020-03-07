# -*- coding: utf-8 -*-
import datetime
import pytz


def strftime(date, input_format, output_format, timezone):
    if type(timezone) is str:
        timezone = pytz.timezone(timezone)
    t = datetime.datetime.strptime(date, input_format)
    converted = t.astimezone(timezone)
    return converted.strftime(output_format)


def double_quote(string):
    return '"' + string + '"'
