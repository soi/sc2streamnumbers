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
# should never be shown, only for calculations
MINIMUM_INTERVAL_ID = 502

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
    cur.execute("SELECT date FROM main_interval \
                 WHERE id > %s ORDER BY date DESC LIMIT 1",
                (MINIMUM_INTERVAL_ID,))
    last_interval_date_tuple = cur.fetchone()

    if last_interval_date_tuple is not None:
        last_interval_date = last_interval_date_tuple[0]
        cur.execute("SELECT count(*) FROM main_interval WHERE id > %s",
                    (MINIMUM_INTERVAL_ID,))
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
    name_tables = ['main_streamtype', 'main_rating', 'main_streamingplatform']

    name_elements = {}
    for table in name_tables:
        cur.execute("SELECT name FROM " + table)
        name_elements[table] = [elem[0] for elem in cur.fetchall()]

    # write the data in the database
    for stream in stream_list:
        if stream['type'] not in name_elements['main_streamtype']:
            cur.execute("INSERT into main_streamtype (name) VALUES (%s) \
                        RETURNING id",
                        (stream['type'],))
            type_id = cur.fetchone()[0]
            name_elements['main_streamtype'].append(stream['type'])
        else:
            cur.execute("SELECT id FROM main_streamtype WHERE name = %s",
                        (stream['type'],))
            type_id = cur.fetchone()[0]

        if stream['rating'] not in name_elements['main_rating']:
            cur.execute("INSERT into main_rating (name) VALUES (%s) \
                        RETURNING id",
                        (stream['rating'],))
            rating_id = cur.fetchone()[0]
            name_elements['main_rating'].append(stream['rating'])
        else:
            cur.execute("SELECT id FROM main_rating WHERE name = %s",
                        (stream['rating'],))
            rating_id = cur.fetchone()[0]

        if stream['streaming_platform'] not in name_elements['main_streamingplatform']:
            cur.execute("INSERT into main_streamingplatform (name) VALUES (%s) \
                        RETURNING id",
                        (stream['streaming_platform'],))
            platform_id = cur.fetchone()[0]
            name_elements['main_streamingplatform'].append(stream['streaming_platform'])
        else:
            cur.execute("SELECT id FROM main_streamingplatform WHERE name = %s",
                        (stream['streaming_platform'],))
            platform_id = cur.fetchone()[0]

        # check if the current stream already exists
        cur.execute("SELECT id, streaming_platform_id, streaming_platform_ident \
                    FROM main_stream \
                    WHERE streaming_platform_id = %s \
                    AND streaming_platform_ident = %s",
                    (
                        platform_id,
                        stream['streaming_platform_ident']
                    ))
        current_stream = cur.fetchone()
        if current_stream is None:
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
        else:
            stream_id = current_stream[0]
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

def get_valid_stream_ids(stream_number_types, interval_snt_id):
    cur.execute("SELECT id, date FROM main_interval \
                ORDER BY date DESC LIMIT %s",
                (
                    str(get_total_number_count(interval_snt_id,
                                               stream_number_types) + 1),
                ))
    relevant_intervals = cur.fetchall()
    early_interval_date = relevant_intervals[len(relevant_intervals) - 1]

    cur.execute("SELECT DISTINCT s.id FROM main_stream s \
                INNER JOIN main_streamnumber sn \
                    ON sn.stream_id = s.id \
                INNER JOIN main_interval i \
                    ON i.id = sn.interval_id \
                WHERE i.date >= %s",
                (
                    str(early_interval_date[1]),
                ))
    return cur.fetchall()

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

    valid_stream_ids = get_valid_stream_ids(stream_number_types,
                                            interval_snt_id)
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
                             ORDER BY i.date DESC \
                             LIMIT %s) as n;",
                        (
                             str(stream_id[0]),
                             str(snt[0] - 1),
                             str(snt[0] - 1),
                             str(snt[1] + 1), # + 1 for the overlapping averages
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
             ORDER BY id DESC")
stream_number_types = cur.fetchall()

# where the magic happends
interval_count = add_missing_intervals(now, stream_number_types)
interval_snt_id = get_interval_snt_id(interval_count + 1,
                                      stream_number_types)
interval_id = insert_new_interval(now, stream_number_types, interval_snt_id)
stream_list = get_stream_dict_from_xml()
insert_raw_stream_numbers(stream_list, interval_id)

if interval_snt_id > 1:
    insert_avg_stream_numbers(interval_id, stream_number_types, interval_snt_id)

# finish
conn.commit()
cur.close()
conn.close()
