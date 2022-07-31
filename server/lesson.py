import json

from flask import Response

import classes
from .helpers import *
from .authentication import get_profile 


def handler(request, school):
	if (profile := get_profile(school, request)) is None:
		return e403()

	return search_lesson(request, school)


def private_handler(request, school):
	if (profile := get_profile(school, request)) is None:
		return e403()
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		return e403()

	if request.method == "GET":
		return search_lesson(request, school)
	if request.method == "POST":
		return create_lesson(request, school)
	if request.method == "DELETE":
		return delete_lesson(request, school)
	

def search_lesson(request, school):
	id = request.args.get("id")
	title = request.args.get("subject")
	cabinet = request.args.get("cabinet")
	teacher = request.args.get("teacher")

	if id is not None and id.isdigit():
		search_result = classes.Lesson.with_id(school, int(id))
	elif title is not None:
		search_result = classes.Lesson.with_subject(school, title)
	elif teacher is not None:
		search_result = classes.Lesson.with_teacher(school, teacher)
	elif cabinet is not None and cabinet.isdigit():
		search_result = classes.Lesson.with_cabinet(school, int(cabinet))
	else:
		return e400()
	
	# Converting the found Cabinet objects into dictionaries
	if isinstance(search_result, list):
		for index in range(len(search_result)):
			search_result[index] = search_result[index].to_old_dict()
	elif isinstance(search_result, classes.Lesson):
		search_result = search_result.to_old_dict()
	else:
		return e404()
	
	response = Response(json.dumps(search_result), status = 200)
	response.headers["Content-Type"] = "application/json"
	return response
	

def create_lesson(request, school):
	data = request.json
	parameters = ["subject", "day", "position", "cabinet",
					"class_number", "class_letter", "teacher"]

	# Are all needed data in the request?
	for p in parameters:
		if p not in data.keys():
			return e400()
		
		if p == "cabinet" and not isinstance(data[p], int):
			return e400()
		elif p == "class_number" and not isinstance(data[p], int):
			return e400()

	# Checking if the provided cabinet exists
	if classes.Cabinet.with_number(school, int(data["cabinet"])) is None:
		return e400()

	# Calling the Classes library and creating a new Lesson object
	new_lesson = classes.Lesson(school)
	
	new_lesson.subject = data["subject"]
	new_lesson.day = int(data["day"])
	new_lesson.position = int(data["position"])
	new_lesson.cabinet = int(data["cabinet"])
	new_lesson.class_number = int(data["class_number"])
	new_lesson.class_letter = data["class_letter"]
	new_lesson.teacher = int(data["teacher"])

	if new_lesson.save_to_db().acknowledged:
	 	return Response("Success", status = 200)
	else:
	 	return e500()


def delete_lesson(request, school):
	data = request.json

	# Checking the number value if it is correct
	if "id" not in data.keys():
		return e400()
	if not isinstance(data["id"], int):
		return e400()
	
	lesson_object = classes.Lesson.with_id(school, data["id"])
	if lesson_object is None:
		return e400()

	if lesson_object.delete().raw_result["ok"]:
		return Response("Success", status = 200)
	else:
		return e500()
