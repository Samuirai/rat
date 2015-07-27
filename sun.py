import ephem
from datetime import datetime, timedelta
import time

def dt_to_ts(dt):
    return (dt - datetime(1970, 1, 1)).total_seconds()

def get_times():
    fred      = ephem.Observer()
    today = datetime.today().replace(hour=15, minute=00, second=00)

    fred.date = today
    #red.date = "2015/7/27 15:00:00"
    fred.lat = str("52.478")
    fred.lon = str("13.404")
    fred.elev = 34
    fred.pressure= 0
    fred.horizon = '-0:34'
    sunrise = fred.previous_rising(ephem.Sun()) #Sunrise
    sunrise = dt_to_ts(sunrise.datetime())
    sunset = fred.next_setting(ephem.Sun()) #Sunset
    sunset = dt_to_ts(sunset.datetime())
    return sunrise, sunset