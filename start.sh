#!/usr/bin/env bash

trap 'killall' INT

killall() {
    trap '' INT TERM
    kill -TERM 0
    wait
}

source env/bin/activate
python manage.py runserver_plus &
celery -A misirlou  worker -l info &
cat