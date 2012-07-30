#!/bin/bash
#-*- coding:utf-8 -*-

psql -U root -c "Copy (select stream_id from main_streamnumber where interval_id = (select max(id) from main_interval) order by stream_id) to stdout" streams
