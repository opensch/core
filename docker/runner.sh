#!/bin/bash

nginx -g 'daemon off;' &
python3 /app/app.fcgi &

wait -n
exit $?
