import json

from flask import Response

import classes
from .helpers import *
from .authentication import get_profile 


def handler(request, school):
	if (profile := get_profile(school, request)) is None:
		return e403()

	return search_cabinet(request, school)


def private_handler(request, school):
	if (profile := get_profile(school, request)) is None:
		return e403()
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		return Response("Insufficient rights.", status = 403)

	if request.method == "GET":
		return search_cabinet(request, school)
	if request.method == "POST":
		return create_cabinet(request, school)
	if request.method == "DELETE":
		return delete_cabinet(request, school)


def search_cabinet(request, school):
	if request.method == "GET":
		floor = request.args.get("floor")
		number = request.args.get("number")

		if number != None and number.isdigit():
			results = classes.Cabinet.with_number(school, int(number))
		elif floor != None and floor.isdigit():
			results = classes.Cabinet.with_floor(school, int(floor))
		else:
			return e400()
		
		if isinstance(results, list):
			results = [cabinet.to_dict() for cabinet in results]
		elif isinstance(results, classes.Cabinet):
			results = results.to_dict()
		else:
			return e404()
		
		response = Response(json.dumps(results), status = 200)
		response.headers["Content-Type"] = "application/json"
		return response


def create_cabinet(request, school):
	data = request.json

	# Are all needed data in the request?
	for p in ["floor", "nearby", "number"]:
		if p not in data.keys():
			return e400()
		if p == "nearby" and not isinstance(data[p], list):
			return e400()
		elif p == "floor" and not isinstance(data[p], int):
			return e400()
		elif p == "number" and not isinstance(data[p], int):
			return e400()

	if classes.Cabinet.with_number(school, data["number"]):
		return e400()

	cabinet = classes.Cabinet(school)
	cabinet.floor = data["floor"]
	cabinet.nearby = data["nearby"]
	cabinet.number = data["number"]

	print(cabinet.__dict__)

	if cabinet.save_to_db().acknowledged:
		return Response("Success", status = 200)
	else:
		return e500()
	

def delete_cabinet(request, school):
	data = request.json

	for p in ["number", "floor"]:
		if p not in data.keys():
			return e400()
		if not isinstance(data[p], int):
			return e400()
	
	query = {"floor": data["floor"], "number": data["number"]}
	results = classes.Cabinet.search(school, query)

	if len(results) == 0:
		return e400()

	if results[0].delete().raw_result["ok"]:
		return Response("Success", status = 200)
	else:
		return e500()
