import pytz
from datetime import datetime

def format_datetime(value, format='%Y-%m-%d %H:%M:%S', timezone='Asia/Kolkata'):
    if value is None:
        return ""

    # Assume the value is a naive datetime in UTC
    utc_dt = pytz.utc.localize(value)

    # Convert to the target timezone
    local_tz = pytz.timezone(timezone)
    local_dt = utc_dt.astimezone(local_tz)

    return local_dt.strftime(format)
