from datetime import datetime
import time, calendar

def to_utc(the_datetime):
    secs = time.mktime(the_datetime.timetuple())
    return datetime.fromtimestamp(time.mktime(time.gmtime(secs)))

def from_utc(the_datetime):
    secs = calendar.timegm(the_datetime.timetuple())
    return datetime.fromtimestamp(time.mktime(time.localtime(secs)))

