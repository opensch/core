import json
import base64
from datetime import datetime

from flask import Response

import classes
from .helpers import *
from .authentication import get_profile 


def handler(request, school, date, lesson):
	if (profile := get_profile(school, request)) is None:
		return e403()
	
	if request.method == "GET":
		return get_homework(school, profile.uid, date, lesson)
	if request.method == "POST":
		return edit_homework(request, school, profile.uid, date, lesson)
	if request.method == "PUT":
		return create_homework(request, school, profile.uid, date, lesson)
	if request.method == "DELETE":
		return delete_homework(request, school, profile.uid, date, lesson)


def get_homework(school, user_id, date, lesson):
	if lesson == "all":
		query = {
			"user_id": profile.uid, 
			"target_date": date, 
		}
		results = classes.Homework.search(school, query)
		results = [item.to_dict() for item in results]
	else:
		results = classes.Homework.fetch(school, user_id, date, int(lesson))
		results = [item.to_dict() for item in results]

	response = Response(json.dumps(results), status = 200)
	response.headers["Content-Type"] = "application/json"
	return response


def edit_homework(request, school, user_id, date, lesson):
	homework = classes.Homework.fetch(school, user_id, date, int(lesson))
	if homework is None:
		return e400()

	homework[0].data = request.get_json()["new_data"]
	if homework[0].save_changes().acknowledged:
		return Response("Success", status = 200)
	else:
		return e500()


def create_homework(request, school, user_id, date, lesson):
	instance = classes.Homework(school)
	instance.user_id = int(user_id)
	instance.lesson_id = int(lesson)
	instance.target_date = date
	instance.data = request.get_json()["data"]

	if instance.save_to_db().acknowledged:
		return Response("Success", status = 200)
	else:
		return e500()


def delete_homework(request, school, user_id, date, lesson):
	homework = classes.Homework.fetch(school, user_id, date, int(lesson))
	if homework is None:
		return e400()
	
	if homework[0].delete().raw_result["ok"]:
		return Response("Success", status = 200)
	else:
		return e500()
