#!/usr/bin/env bash

source .env/bin/activate
python -m http.server 8888 &
testServer=$!
coverage run manage.py test
coverage report
kill -9 "$testServer"
