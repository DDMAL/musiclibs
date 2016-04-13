#!/usr/bin/env bash

source .env/bin/activate
coverage run manage.py test
coverage report
