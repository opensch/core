#!/usr/bin/python
import sys
from flup.server.fcgi import WSGIServer
from main import app

sys.path.insert(0,"/app/")

if __name__ == '__main__':
    WSGIServer(app, bindAddress='/tmp/openSchool-fcgi.sock').run()
