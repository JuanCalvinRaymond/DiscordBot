from datetime import datetime, timedelta
import time

def timestampConverter(arg):
        unix_timestamp = int(time.mktime(arg.timetuple()))
        return unix_timestamp