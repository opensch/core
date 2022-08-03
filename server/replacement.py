import json

from flask import Response

import classes
from .helpers import *
from .authentication import get_profile


def handler(request, school):
    if (profile := get_profile(school, request)) is None:
        return e403()

    return get_replacements(request, school)


def private_handler(request, school):
    if (profile := get_profile(school, request)) is None:
        return e403()
    if "role" not in profile.flags or profile.flags["role"] == 0:
        return e403()

    if request.method == "GET":
        return get_replacements(request, school)
    if request.method == "POST":
        return create_replacement(request, school)
    if request.method == "DELETE":
        return delete_replacement(request, school)


def get_replacements(request, school):
    date = request.args.get("date")
    results = classes.Replacement.with_date(school, date)

    if len(results) == 0:
        return e404()

    results = [item.to_dict() for item in results]
    return Response(json.dumps(results), status=200)


def create_replacement(request, school):
    data = request.get_json()
    instance = classes.Replacement(school)

    instance.lesson_id = data["lesson_id"]
    instance.date = data["date"]
    instance.subject = data["subject"] if "subject" in data.keys() else None
    instance.position = data["position"] if "position" in data.keys() else None
    instance.cabinet = data["cabinet"] if "cabinet" in data.keys() else None
    instance.teacher = data["teacher"] if "teacher" in data.keys() else None

    if instance.save_to_db().acknowledged:
        return Response("Success", status=200)
    else:
        return e400()


def delete_replacement(request, school):
    data = request.get_json()
    query = {"date": data["date"], "lesson_id": data["lesson_id"]}
    replacement = classes.Replacement.search(school, query)

    if len(replacement) != 1:
        return e403()

    if replacement[0].delete().raw_result["ok"]:
        return Response("Success", status=200)
    else:
        return e400()
