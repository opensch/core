import classes
import json

from datetime import datetime
import time

import requests
from tqdm import tqdm


def getTime():
    n = {}
    with open("time.json") as f:
        n = json.loads(f.read())
    return n


def fix(time, current):
    time = time.replace(day=current.day, month=current.month, year=current.year)
    return time


wasToday = {}
lastReset = 0


def sendFirebase(token, title, content):
    data = {"to": token, "notification": {"title": title, "body": content}}
    requests.post(
        "https://fcm.googleapis.com/fcm/send",
        headers={
            "Content-Type": "application/json",
            "Authorization": "key=" + classes.Config().googleFCM,
        },
        data=json.dumps(data),
    )


def sendToUser(user, title, content):
    for x in user.tokens:
        sendFirebase(x, title, content)


def findNextLesson(timetable, _class):
    curDate = datetime.now()
    times = getTime()

    _next = None

    for x in range(len(timetable.lessons)):
        startTime = times[_class][x].split("-")[0]
        startTime = fix(datetime.strptime(startTime, "%H:%M"), curDate)

        if startTime >= curDate and _next == None:
            if timetable.lessons[x] != "-":
                _next = timetable.lessons[x]

    return _next


def getTimetableNotification(_class):
    times = getTime()
    nonDefault = []

    for x in times.keys():
        if x != "default":
            nonDefault.append(x)

    allUsers = classes.User.find("", "all")
    for i in tqdm(allUsers):
        if i.notifParams["10min"] == True and len(i.tokens) != 0:
            userClass = "default"
            if str(i.classNumber) in nonDefault:
                userClass = str(i.classNumber)

            if userClass == _class:
                userTimetable = classes.Timetable.createTimetable(i, datetime.now())
                lesson = findNextLesson(userTimetable, userClass)

                if lesson != None:
                    _title = "🏫 Скоро урок"
                    _content = "Через 10 минут у вас начинается " + lesson.title

                    sendToUser(i, _title, _content)


def checkTimes(times):
    curDate = datetime.now()

    for i in times.keys():
        if i not in wasToday:
            wasToday[i] = []

        for x in times[i]:
            if x in wasToday[i]:
                continue
            startTime = x.split("-")[0]
            startTime = fix(datetime.strptime(startTime, "%H:%M"), curDate)
            if startTime >= curDate:
                diff = (startTime - curDate).total_seconds()
                if diff <= 600:
                    print("Send 10minute push to " + i)
                    getTimetableNotification(i)
                    wasToday[i].append(x)
                    print("Worker end")


times = getTime()

while True:
    checkTimes(times)  # Send push notification with lesson start text

    ####### ######## #####
    # Reset watchdog lock#
    ####### ######## #####

    currentDate = datetime.now()
    if currentDate.hour == 0:
        if currentDate.day != lastReset:
            wasToday = {}
            lastReset = currentDate.day

    time.sleep(1)
