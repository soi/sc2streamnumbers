#!/bin/bash
#-*- coding:utf-8 -*-

psql -U root -c "drop database streams;" postgres; psql -U root -c "create database streams" postgres;
ssh soi@178.77.100.105 "pg_dump -U streams > /home/soi/dumps/main_dump.sql"
rsync -aP soi@178.77.100.105:/home/soi/dumps/main_dump.sql /home/soi/git/streams/main_dump_remote.sql
psql -U root -f /home/soi/git/streams/main_dump_remote.sql
