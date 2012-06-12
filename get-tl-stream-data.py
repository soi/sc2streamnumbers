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
DBNAME = "streams"
DBUSER = "root"
# can cause problems when < 3 min
QUERY_INTERVAL_MIN = 5

# save the time of the script at the start
now = datetime.datetime.now(pytz.timezone('Europe/Berlin'))

# retrive the xml file
request = urllib2.Request(URL)
request.add_header('Accept-encoding', 'gzip')
request.add_header('User-agent', 'Custom User Agent')
response = urllib2.urlopen(request)
response_str = response.read()

# save the xml file so we always have it for later investigation
external_file = open(XML_FILES_FOLDER + 'tl_livestreams_' + str(int(time.time())) + '.gz', "wb")
external_file.write(response_str)
external_file.close();

# unzip it
buf = StringIO.StringIO(response_str)
f = gzip.GzipFile(fileobj=buf)
# f = open('tl.xml')
xml_data = f.read()

# parse the data
parser = ET.XML(xml_data)

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

# retrieve the list of the current types and names
conn = psycopg2.connect("dbname=" + DBNAME + " user=" + DBUSER)
cur = conn.cursor()

cur.execute("SELECT date FROM main_interval ORDER BY date DESC LIMIT 1")
last_interval_date = cur.fetchone()[0]
min_interval_delta = now - datetime.timedelta(minutes=(QUERY_INTERVAL_MIN + 2))

# fill a possible gap with blank intervals
while last_interval_date < min_interval_delta:
    last_interval_date = last_interval_date + datetime.timedelta(minutes=5)
    cur.execute("INSERT into main_interval (date) VALUES (%s)",
                last_interval_date)

cur.execute("SELECT name FROM main_stream")
names = [elem[0] for elem in cur.fetchall()]

cur.execute("SELECT name FROM main_streamtype")
types = [elem[0] for elem in cur.fetchall()]

# write the data in the database
cur.execute("INSERT into main_interval (date) VALUES (%s) RETURNING id", now)
interval_id = cur.fetchone()[0]

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

    cur.execute("INSERT into main_streamnumber (stream_id, interval_id, \
                stream_type_id, number) VALUES (%s,%s,%s,%s)",
                (
                     str(stream_id),
                     str(interval_id),
                     str(type_id),
                     stream['number']
                ))

    conn.commit()

cur.close()
conn.close()
