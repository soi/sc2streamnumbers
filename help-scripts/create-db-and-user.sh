#!/bin/bash
#-*- coding:utf-8 -*-

NAME=streams

if [[ $(whoami) != "postgres" ]]; then
	echo "Must be run as user postgres"
	exit 1
fi

psql -c "create database $NAME;" postgres

echo "Password for the user $NAME:"
read pw

psql -c "Create user $NAME with password '$pw';" postgres
psql -c "Grant all privileges on database $NAME to $NAME" postgres
