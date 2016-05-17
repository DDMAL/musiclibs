#!/usr/bin/env bash

# Ctrl+C will kill all the processes started by this script.
trap 'killall' INT
killall() {
    trap '' EXIT INT TERM
    pkill -P $$
    wait
}

# Start all the dev servers in async.
source .env/bin/activate
python manage.py runserver_plus &
celery -A misirlou  worker -l info 
celery -A misirlou beat &
cat
