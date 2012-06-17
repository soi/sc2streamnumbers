#!/usr/bin/python

import pytz
import psycopg2
import datetime

DB_NAME = "streams"
DB_USER = "root"
INTERVAL_DAY_COUNT = 288
EARLY_INTERVAL_DATE = datetime.datetime(2012, 6, 1, 00, 00, 00, tzinfo=pytz.timezone('Europe/Berlin'))

# db connection
conn = psycopg2.connect("dbname=" + DB_NAME + " user=" + DB_USER)
cur = conn.cursor()

cur.execute("SELECT date, stream_number_type_id from main_interval ORDER BY date ASC LIMIT " + str(INTERVAL_DAY_COUNT))
day_intervals = [[elem[0], elem[1],] for elem in cur.fetchall()]

last_valid_date = day_intervals[0][0]

while last_valid_date > EARLY_INTERVAL_DATE:
    for interval in day_intervals:
        interval[0] = interval[0] - datetime.timedelta(days=1)
        cur.execute("INSERT into main_interval (stream_number_type_id, date) \
                     VALUES (%s, %s)",
                    (
                        interval[1],
                        interval[0],
                    ))
    last_valid_date = day_intervals[0][0]

# finish
conn.commit()
cur.close()
conn.close()
