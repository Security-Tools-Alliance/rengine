#!/bin/bash

gunicorn reNgine.wsgi:application -w 8 --bind 0.0.0.0:8000 --limit-request-line 0

exec "$@"