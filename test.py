import time
from datetime import date

time_till = date(2018, 3, 26)

unixtime = time.mktime(time_till.timetuple())
print(time_till)