import json
import hashlib

from flask import Response

import classes
from .helpers import *
from .authentication import get_profile
from datetime import datetime


def notifications_handler(request, school):
    if (profile := get_profile(school, request)) is None:
        return e403()

    if request.method == "GET":
        response = Response(json.dumps(profile.notifParams), status=200)
        response.headers["Content-Type"] = "application/json"
        return response

    elif request.method == "POST":
        args = request.json
        has_changes = False
        params = ["10min", "homework", "homeworkTime", "replacements"]

        for key, value in args.items():
            if key not in params:
                return e400()
            if key != "homeworkTime":
                compareTo = bool
            else:
                compareTo = int

            if not isinstance(value, compareTo):
                return e400()

            has_changes = True
            profile.notifParams[key] = value

        if has_changes:
            profile.save_changes()
            response_json = {"status": "ok", "c": profile.notifParams}
            response = Response(json.dumps(response_json), status=200)
            response.headers["Content-Type"] = "application/json"
            return response
        else:
            print("Not changed")
            return e400()

def signature(pushToken, username, title, body, time):
	# create sha256 signature 
	signature = hashlib.sha256()
	signature.update( (pushToken+username+title+body+str(time)).encode() )
	return signature.hexdigest()

def pushSignature(request, school):
    args = request.json

    params = ["signature", "token", "title", "body"]

    for key, value in args.items():
        if key not in params:
            return e400()

    currentDay = datetime.now().day
    currentHour = datetime.now().hour
    time = currentDay + currentHour

    users = school.database.users.find({"tokens": args['token']})
    for i in users:
        login = i['login']
        testSignature = signature(args['token'], login, args['title'], args['body'], time)

        if testSignature == args['signature']:
            return Response(login, status=200)
    
    return Response("None", status=200)


def passwd(request, school):
    if (profile := get_profile(school, request)) is None:
        return e403()

    args = request.json

    if "old" in args.keys() and "new" in args.keys():
        h = hashlib.sha512(args["old"].encode())
        if profile.password == h.hexdigest():
            profile.password = hashlib.sha512(args["new"].encode()).hexdigest()
            profile.save_changes()

            response = Response(json.dumps({"status": "ok"}), status=200)
            return response
        else:
            return e403()
    else:
        return e400()


def addToken(request, school):
    if (profile := get_profile(school, request)) is None:
        return e403()

    args = request.form

    if len(args['token'].split("|")) == 1:
        args['token'] = "https://push.openschool.cc|"+args['token']

    if "token" in args:
        if args["token"] not in profile.tokens:
            profile.tokens.append(args["token"])
            profile.save_changes()

        response = Response(json.dumps({"status": "ok"}), status=200)
        response.headers["Content-Type"] = "application/json"
        return response
    else:
        return e400()
