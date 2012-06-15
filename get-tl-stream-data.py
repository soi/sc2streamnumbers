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

URL = 'http://www.teamliquid.net/video/streams/?filter=live&xml=1'
XML_FILES_FOLDER = '/home/felix/git/streams/xml/'
DB_NAME = "streams"
DB_USER = "root"
# can cause problems when < 3 min
QUERY_INTERVAL_MIN = 5

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

def get_tl_xml_file():
    """fetches the tl xml stream list and returns it as string"""
    request = urllib2.Request(URL)
    request.add_header('Accept-encoding', 'gzip')
    request.add_header('User-agent', 'Custom User Agent')
    response = urllib2.urlopen(request)
    response_str = response.read()

    # save the xml file so we always have it for later investigation
    external_file = open(XML_FILES_FOLDER + \
                         'tl_livestreams_' +
                         str(int(time.time())) +
                         '.gz',
                         "wb")
    external_file.write(response_str)
    external_file.close();

    # unzip it
    buf = StringIO.StringIO(response_str)
    f = gzip.GzipFile(fileobj=buf)
    # f = open('tl.xml')
    return f.read()

def get_stream_dict_from_xml():
    """parses the xml file and creates a corresponding python dict"""
    parser = ET.XML(get_tl_xml_file())

    stream_list = []

    for stream in parser:
        latest_stream = {}
        if stream.get('type') is None:
            latest_stream['type'] = 'Default'
        else:
            latest_stream['type'] = stream.get('type')
        if stream.get('viewers') is None:
            latest_stream['number'] = '0'
        else:
            latest_stream['number'] = stream.get('viewers')

        channel = stream.find('channel')
        latest_stream['name'] = channel.get('title')

        stream_list.append(latest_stream)
    return stream_list

def insert_new_interval(now, stream_number_types, interval_snt_id):
    cur.execute("INSERT into main_interval (stream_number_type_id, date) \
                 VALUES (%s, %s) RETURNING ID",
                (interval_snt_id, now))
    interval_id = cur.fetchone()[0]
    return interval_id

def add_missing_intervals(now, stream_number_types):
    cur.execute("SELECT date FROM main_interval ORDER BY date DESC LIMIT 1")
    last_interval_date_tuple = cur.fetchone()

    if last_interval_date_tuple is not None:
        last_interval_date = last_interval_date_tuple[0]
        cur.execute("SELECT count(*) FROM main_interval")
        interval_count = cur.fetchone()[0]

        min_interval_delta = now - datetime.timedelta(minutes=(QUERY_INTERVAL_MIN + 2))
        # fill a possible gap with blank intervals
        while last_interval_date < min_interval_delta:
            last_interval_date = last_interval_date + datetime.timedelta(minutes=5)
            # increase before insert so the calculation fits
            interval_count = interval_count + 1
            cur.execute("INSERT into main_interval (stream_number_type_id, date) \
                         VALUES (%s, %s)",
                        (
                            get_interval_snt_id(interval_count, stream_number_types),
                            last_interval_date
                        ))

        conn.commit()
        return interval_count
    else:
        return 0

def insert_raw_stream_numbers(stream_list, interval_id):
    cur.execute("SELECT name FROM main_stream")
    names = [elem[0] for elem in cur.fetchall()]

    cur.execute("SELECT name FROM main_streamtype")
    types = [elem[0] for elem in cur.fetchall()]

    # write the data in the database
    for stream in stream_list:
        if stream['type'] not in types:
            cur.execute("INSERT into main_streamtype (name) VALUES (%s)",
                        (stream['type'],))
            types.append(stream['type'])
        if stream['name'] not in names:
            cur.execute("INSERT into main_stream (name) VALUES (%s)",
                        (stream['name'],))
            names.append(stream['name'])

        # get the id of the type and name
        cur.execute("SELECT id FROM main_stream WHERE name = %s",
                    (stream['name'],))
        stream_id = cur.fetchone()[0]

        cur.execute("SELECT id FROM main_streamtype WHERE name = %s",
                    (stream['type'],))
        type_id = cur.fetchone()[0]


        # insert the raw one
        cur.execute("INSERT into main_streamnumber (stream_id, interval_id, \
                    stream_type_id, stream_number_type_id, number) \
                    VALUES (%s,%s,%s,%s,%s)",
                    (
                         str(stream_id),
                         str(interval_id),
                         str(type_id),
                         '1',
                         stream['number']
                    ))
        conn.commit()

def insert_avg_stream_numbers(interval_id,
                              stream_number_types,
                              interval_snt_id):

    cur.execute("SELECT id FROM main_stream")
    all_stream_ids = cur.fetchall()

    # put the list of applying snts together
    valid_snts = []
    for snt in stream_number_types:
        if snt[0] == interval_snt_id:
            # list without the raw one
            valid_snts = stream_number_types[stream_number_types.index(snt):-1]
            break

    for stream_id in all_stream_ids:
        for snt in valid_snts:
            # calculate from the averages from the next bigger resolution
            cur.execute("SELECT avg(n.number) FROM \
                            (SELECT sn.number FROM main_interval as i \
                             LEFT JOIN main_streamnumber as sn \
                                ON (sn.interval_id = i.id \
                                    AND sn.stream_id = %s \
                                    AND sn.stream_number_type_id = %s) \
                             ORDER BY i.date DESC \
                             LIMIT %s) as n;",
                        (
                             str(stream_id[0]),
                             str(snt[0] - 1),
                             str(snt[0] - 1),
                             str(snt[1]),
                        ))
            snt_stream_number = cur.fetchone()[0]

            if snt_stream_number is not None:
                cur.execute("INSERT into main_streamnumber (stream_id, \
                            interval_id, stream_type_id, \
                            stream_number_type_id, number) \
                            VALUES (%s,%s,%s,%s,%s)",
                            (
                                 str(stream_id[0]),
                                 str(interval_id),
                                 '1',
                                 str(snt[0]),
                                 str(int(snt_stream_number)),
                            ))

                conn.commit()


# save the time of the script at the start
now = datetime.datetime.now(pytz.timezone('Europe/Berlin'))

# db connection
conn = psycopg2.connect("dbname=" + DB_NAME + " user=" + DB_USER)
cur = conn.cursor()

cur.execute("SELECT id, number_count FROM main_streamnumbertype \
             ORDER BY number_count DESC")
stream_number_types = cur.fetchall()

# where the magic happends
interval_count = add_missing_intervals(now, stream_number_types)
interval_snt_id = get_interval_snt_id(interval_count + 1,
                                      stream_number_types)
interval_id = insert_new_interval(now, stream_number_types, interval_snt_id)
stream_list = get_stream_dict_from_xml()
insert_raw_stream_numbers(stream_list, interval_id)
insert_avg_stream_numbers(interval_id, stream_number_types, interval_snt_id)

# finish
conn.commit()
cur.close()
conn.close()
