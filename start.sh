#!/usr/bin/env bash

VIRTUAL_ENV=.env
HOST=localhost
PORT=8000

for i in "$@"
do
case $i in
    --env=*)
    VIRTUAL_ENV="${i#*=}"
    shift
    ;;
    --host=*)
    HOST="${i#*=}"
    shift
    ;;
    --port=*)
    PORT="${i#*=}"
    shift
    ;;
    *)
        # unknown option
    ;;
esac
done

# Ctrl+C will kill all the processes started by this script.
trap 'killall' INT
killall() {
    trap '' EXIT INT TERM
    pkill -P $$
    wait
}

# Start all the dev servers in async.
source "$VIRTUAL_ENV/bin/activate"
python manage.py runserver_plus $HOST:$PORT &
celery -A misirlou  worker -l info
cat
