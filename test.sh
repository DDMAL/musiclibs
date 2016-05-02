#!/usr/bin/env bash

source .env/bin/activate
python -m http.server 8888 2> /dev/null &
testServer=$!
coverage run manage.py test
coverage report
kill -9 "$testServer"
