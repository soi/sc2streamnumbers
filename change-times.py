#!/usr/bin/python

import sys
import gzip
import time
import pytz
import urllib2
import StringIO
import psycopg2
import datetime
import xml.etree.ElementTree as ET

DB_NAME = "streams"
DB_USER = "root"
# can cause problems when < 3 min
QUERY_INTERVAL_MIN = 5
# should never be shown, only for calculations
MINIMUM_INTERVAL_ID = 502
# MINIMUM_INTERVAL_ID = 0

def get_total_number_count(snt_id, stream_number_types):
    """Calculates the raw number count of a snt.
    stream_number_types are supposed to be ordered with the biggest first"""
    count = 1
    for snt in stream_number_types:
        if snt[0] <= snt_id:
            count = count * snt[1]
    return count

def get_interval_snt_id(interval_count, stream_number_types):
    """checks if the current interval count is special.
    stream_number_types are supposed to be ordered with the biggest first
    returns the stream_number_type id.
    last number is always 1 so 1 is the default return id"""
    for snt in stream_number_types:
        number_count = get_total_number_count(snt[0], stream_number_types)
        if interval_count % number_count == 0:
            return snt[0]

# db connection
conn = psycopg2.connect("dbname=" + DB_NAME + " user=" + DB_USER)
cur = conn.cursor()

cur.execute("SELECT id, number_count FROM main_streamnumbertype \
             ORDER BY id DESC")
stream_number_types = cur.fetchall()

cur.execute("SELECT id FROM main_stream")
all_stream_ids = cur.fetchall()

cur.execute("SELECT id, date FROM main_interval where id > %s order by date asc",
            (MINIMUM_INTERVAL_ID,))
all_intervals = cur.fetchall()

interval_count = 0
while interval_count < len(all_intervals):

    interval = all_intervals[interval_count]
    interval_count += 1

    print "\ninterval = " + str(interval[0])

    interval_snt_id = get_interval_snt_id(interval_count, stream_number_types)

    print "interval_snt_id = " + str(interval_snt_id)

    if interval_snt_id > 1:
        cur.execute("Update main_interval set stream_number_type_id = %s where id = %s",
                    (
                        interval_snt_id,
                        interval[0],
                    ))
        conn.commit()

        valid_snts = []
        for snt in stream_number_types:
            if snt[0] == interval_snt_id:
                # list without the raw one
                valid_snts = stream_number_types[stream_number_types.index(snt):-1]
                # with the lowest at front now
                valid_snts.reverse()
                break

        cur.execute("select id, date from main_interval where date <= %s order by date desc limit %s",
                    (
                        str(interval[1]),
                        get_total_number_count(valid_snts[len(valid_snts) -1][0], stream_number_types) + 1
                    ))
        relevant_intervals = cur.fetchall()
        early_interval_date = relevant_intervals[len(relevant_intervals) - 1]

        print "interval start = " + str(early_interval_date)
        print "interval end = " + str(interval[1])

        cur.execute("select distinct s.id from main_stream s join main_streamnumber sn on sn.stream_id = s.id join main_interval i on i.id = sn.interval_id where i.date <= %s and i.date >= %s",
                    (
                        str(interval[1]),
                        str(early_interval_date[1])
                    ))
        valid_stream_ids = cur.fetchall()

        print "stream count = " + str(len(valid_stream_ids))

        for stream_id in valid_stream_ids:
            for snt in valid_snts:
                # calculate from the averages from the next bigger resolution
                cur.execute("SELECT avg(n.number) FROM \
                                (SELECT sn.number FROM main_interval as i \
                                 LEFT JOIN main_streamnumber as sn \
                                    ON (sn.interval_id = i.id \
                                        AND sn.stream_id = %s \
                                        AND sn.stream_number_type_id = %s) \
                                 WHERE i.stream_number_type_id >= %s \
                                    AND i.date <= %s \
                                 ORDER BY i.date DESC \
                                 LIMIT %s) as n;",
                            (
                                 str(stream_id[0]),
                                 str(snt[0] - 1),
                                 str(snt[0] - 1),
                                 str(interval[1]),
                                 str(snt[1] + 1),
                            ))
                snt_stream_number = cur.fetchone()[0]

                if snt_stream_number is not None:
                    cur.execute("INSERT into main_streamnumber (stream_id, \
                                interval_id, stream_type_id, \
                                stream_number_type_id, number) \
                                VALUES (%s,%s,%s,%s,%s)",
                                (
                                     str(stream_id[0]),
                                     str(interval[0]),
                                     '1',
                                     str(snt[0]),
                                     str(int(snt_stream_number)),
                                ))

                    conn.commit()


cur.close()
conn.close()
