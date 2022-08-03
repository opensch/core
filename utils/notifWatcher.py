import sys

sys.path.append("..")

from config import Config

import classes
import requests
import json
import os


def sendFirebase(token, title, content):
    data = {"to": token, "notification": {"title": title, "body": content}}
    requests.post(
        "https://fcm.googleapis.com/fcm/send",
        headers={
            "Content-Type": "application/json",
            "Authorization": "key=" + Config().googleFCM,
        },
        data=json.dumps(data),
    )


def sendPush(title, content):
    db = classes.createMongo().users
    db = db.find()
    for i in db:
        tokens = i["tokens"]
        for c in tokens:
            sendFirebase(c, title, content)


if os.path.exists("lastNews") is not True:
    with open("lastNews", "w") as f:
        f.write("")

with open("cdn/news.json") as f:
    jsonData = json.loads(f.read())

with open("lastNews", "r") as f:
    raw = f.read()
    if raw == "":
        lastJson = {}
        lastJson["content"] = ""
    else:
        lastJson = json.loads(raw)

if jsonData[0]["content"] != lastJson["content"]:
    if jsonData[0]["important"] == True:
        sendPush("Срочная новость", jsonData[0]["title"])

        with open("lastNews", "w") as f:
            f.write(json.dumps(jsonData[0]))
