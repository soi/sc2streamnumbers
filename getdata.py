#!/usr/bin/python

import psycopg2
import sys

dbname = "streams"
user = "root"

conn = psycopg2.connect("dbname=" + dbname + " user=" + user)
cur = conn.cursor()

cur.execute("")

cur.close()
conn.close()
