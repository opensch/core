import json

from flask import Response

from .helpers import *
from .authentication import get_profile


def getTime(request, school):
    if (profile := get_profile(school, request)) is None:
        return e403()

    number = request.args.get("number")
    if number is None:
        return e400()

    with open("time.json") as timeDataFile:
        timeData = json.loads(timeDataFile.read())

    timeObj = timeData["default"]
    if str(profile.classNumber) in timeData:
        timeObj = timeData[str(profile.classNumber)]
    print(timeObj)

    try:
        ret = timeObj[int(number)]
    except Exception:
        return e400()

    return ret


def getTimes(request, school):
    if (profile := get_profile(school, request)) is None:
        return e403()

    with open("time.json") as timeDataFile:
        timeData = json.loads(timeDataFile.read())

    timeObj = timeData["default"]
    if str(profile.classNumber) in timeData:
        timeObj = timeData[str(profile.classNumber)]

    try:
        ret = Response(json.dumps(timeObj), status=200)
        ret.headers["Content-Type"] = "application/json"
    except Exception:
        return e400()

    return ret
