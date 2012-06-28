#!/usr/bin/python

import os
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

def get_stream_dict_from_xml(raw):
    """parses the xml file and creates a corresponding python dict"""
    parser = ET.XML(raw)

    stream_list = []
    stream_props = [
        {
            'name' : 'type',
            'default': 'Default',
        },
        {
            'name' : 'viewers',
            'default': '0',
        },
        {
            'name' : 'rating',
            'default': 'Default',
        },
    ]
    for stream in parser:
        latest_stream = {}
        for prop in stream_props:
            if stream.get(prop['name']) is None:
                latest_stream[prop['name']] = prop['default']
            else:
                latest_stream[prop['name']] = stream.get(prop['name'])

        # channel properties
        channel = stream.find('channel')
        if channel is None:
            continue
        else:
            if channel.get('title') is None:
                continue
            else:
                latest_stream['name'] = channel.get('title')
            if channel.get('type') is None:
                latest_stream['streaming_platform'] = 'Default'
            else:
                latest_stream['streaming_platform'] = channel.get('type')
            if channel.text is None:
                latest_stream['streaming_platform_ident'] = ''
            else:
                latest_stream['streaming_platform_ident'] = channel.text

        # link properties
        link = stream.find('link')
        if link is None:
            continue
        else:
            if link.text is None or link.get('type') != 'embed':
                latest_stream['tl_stream_link'] = ''
            else:
                latest_stream['tl_stream_link'] = link.text

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
        return interval_count
    else:
        return 0

def insert_raw_stream_numbers(stream_list, interval_id):
    tables = ['main_stream', 'main_streamtype', 'main_rating', 'main_streamingplatform']

    all_elements = {}
    for table in tables:
        cur.execute("SELECT name FROM " + table)
        all_elements[table] = [elem[0] for elem in cur.fetchall()]

    # write the data in the database
    for stream in stream_list:
        if stream['type'] not in all_elements['main_streamtype']:
            cur.execute("INSERT into main_streamtype (name) VALUES (%s) \
                        RETURNING id",
                        (stream['type'],))
            type_id = cur.fetchone()[0]
            all_elements['main_streamtype'].append(stream['type'])
        else:
            cur.execute("SELECT id FROM main_streamtype WHERE name = %s",
                        (stream['type'],))
            type_id = cur.fetchone()[0]

        if stream['rating'] not in all_elements['main_rating']:
            cur.execute("INSERT into main_rating (name) VALUES (%s) \
                        RETURNING id",
                        (stream['rating'],))
            rating_id = cur.fetchone()[0]
            all_elements['main_rating'].append(stream['rating'])
        else:
            cur.execute("SELECT id FROM main_rating WHERE name = %s",
                        (stream['rating'],))
            rating_id = cur.fetchone()[0]

        if stream['streaming_platform'] not in all_elements['main_streamingplatform']:
            cur.execute("INSERT into main_streamingplatform (name) VALUES (%s) \
                        RETURNING id",
                        (stream['streaming_platform'],))
            platform_id = cur.fetchone()[0]
            all_elements['main_streamingplatform'].append(stream['streaming_platform'])
        else:
            cur.execute("SELECT id FROM main_streamingplatform WHERE name = %s",
                        (stream['streaming_platform'],))
            platform_id = cur.fetchone()[0]

        # add or update the current stream
        if stream['name'] not in all_elements['main_stream']:
            cur.execute("INSERT INTO main_stream (name, rating_id, \
                        streaming_platform_id, streaming_platform_ident, \
                        tl_stream_link) VALUES (%s,%s,%s,%s,%s) RETURNING id",
                        (
                            stream['name'],
                            str(rating_id),
                            str(platform_id),
                            stream['streaming_platform_ident'],
                            stream['tl_stream_link']
                        ))
            stream_id = cur.fetchone()[0]
            all_elements['main_stream'].append(stream['name'])
        else:
            cur.execute("SELECT id FROM main_stream WHERE name = %s",
                        (stream['name'],))
            stream_id = cur.fetchone()[0]
            cur.execute("UPDATE main_stream SET \
                        rating_id = %s, streaming_platform_id = %s, \
                        streaming_platform_ident = %s, tl_stream_link = %s \
                        WHERE id = %s",
                        (
                            str(rating_id),
                            str(platform_id),
                            stream['streaming_platform_ident'],
                            stream['tl_stream_link'],
                            str(stream_id)
                        ))

        # insert the raw stream number
        cur.execute("INSERT into main_streamnumber (stream_id, interval_id, \
                    stream_type_id, stream_number_type_id, number) \
                    VALUES (%s,%s,%s,%s,%s)",
                    (
                        str(stream_id),
                        str(interval_id),
                        str(type_id),
                        '1',
                        stream['viewers']
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
            # with the lowest at front now
            valid_snts.reverse()
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
                             WHERE i.stream_number_type_id >= %s \
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


def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))

# db connection
conn = psycopg2.connect("dbname=" + DB_NAME + " user=" + DB_USER)
cur = conn.cursor()

cur.execute("SELECT id, number_count FROM main_streamnumbertype \
             ORDER BY id DESC")
stream_number_types = cur.fetchall()

for f in sorted_ls(XML_FILES_FOLDER):
    print "\nworking on " + f

    fname = XML_FILES_FOLDER + f
    fg = gzip.GzipFile(filename=fname)
    ftime = os.path.getmtime(fname)
    now = datetime.datetime.fromtimestamp(int(ftime))

    # where the magic happends
    interval_count = add_missing_intervals(now, stream_number_types)
    interval_snt_id = get_interval_snt_id(interval_count + 1,
                                          stream_number_types)

    print "snt_id = " + str(interval_snt_id)
    print "time = " + str(now)

    interval_id = insert_new_interval(now, stream_number_types, interval_snt_id)
    stream_list = get_stream_dict_from_xml(fg.read())
    insert_raw_stream_numbers(stream_list, interval_id)
    insert_avg_stream_numbers(interval_id, stream_number_types, interval_snt_id)

# finish
conn.commit()
cur.close()
conn.close()


