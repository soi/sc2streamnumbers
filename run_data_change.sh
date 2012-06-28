#!/bin/bash
#-*- coding:utf-8 -*-

psql -U root -c "drop database streams;" postgres;
psql -U root -c "create database streams;" postgres;

psql -U root -f main_dump.sql streams
psql -U root -c "delete from main_streamnumber where interval_id < 503 or stream_number_type_id > 1; delete from main_interval where id < 503; update main_interval set stream_number_type_id = 1" streams
./change-times.py
./add_xml.py

