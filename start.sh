#!/usr/bin/env bash

netstat -luntp|grep 10001|awk '{print $NF}'|awk -F/ '{print "kill -9 "$1}'|sh
git pull

source /opt/py3/bin/activate
#python3 manage.py makemigrations
#python3 manage.py migrate


#nohup uwsgi --http :10001 --chdir .  --wsgi-file  ./Fiction/wsgi.py > django.log 2>&1 &
#uwsgi --socket 127.0.0.1:8000 --chdir . --wsgi-file ./Fiction/wsgi.py --daemonize django_socket.log
uwsgi --http :10001 --chdir .  --wsgi-file  ./Fiction/wsgi.py --daemonize uwsgi.log
#python3 manage.py collectstatic