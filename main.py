from calendar import c
import json
from flask import Flask, Response, request
from routes import routingMap
from config import Config
import os, re

from functions import e400, e403, e404, e405

if os.getenv("KUBERNETES") == "1":
	import kubernetesConfig

app = Flask(__name__)

def startup ():
	"""
	This is the initialization function. It is run first to prepare
	the environment before starting up the Flask application, like folder
	creation, configuration file checking, etc.
	"""
	  
	# Creating folders to store OAuth codes
	if os.path.isdir("codes") != True:
		os.mkdir("codes")
	if os.path.isdir("tokens") != True:
		os.mkdir("tokens")
	if os.path.isdir("tokens/access") != True:
		os.mkdir("tokens/access")
	if os.path.isdir("tokens/refresh") != True:
		os.mkdir("tokens/refresh")
		
	# Checking the configuration file for the current mode
	mode = Config().mode
	key = Config().clientSecret 
	
	if mode == "production":   
		if len(key) < 16:
			raise "Client secret key too short (16 chars minimum)"
		else:
			debugging = False
	
	elif mode == "development":
		debugging = True 
	else:
		raise f"Mode '{mode}' unknown. Waiting for 'production' or 'development'"
	
	# Starting up the Flask application
	app.run(host = "0.0.0.0", port = Config().port, debug = debugging)


def addHeaders(response):
	response.headers['Access-Control-Allow-Origin'] = "*"
	response.headers['Access-Control-Allow-Headers'] = '*'
	response.headers['Access-Control-Allow-Methods'] = '*'
	
	try:
		json.loads(response.get_data().decode())
		response.headers['Content-type'] = 'application/json'
	except Exception:
		pass

	return response

def findPath(path):
	path = path.split("/")
	for i in routingMap.keys():
		checkPath = re.sub('<.*?>', '', i)

		if checkPath == '/'.join(path):
			return routingMap[i], i

		pathCheck = path.copy()
		for x in reversed(range(len(path))):
			if "<path:" in i:
				checkPath = checkPath.replace("//", "")
				del pathCheck[x]
				if len(pathCheck) == 1:
					pathCheck.append('')
			else:
				pathCheck[x] = ""

			if checkPath == '/'.join(pathCheck):
				return routingMap[i], i

	return None

def parseArgs(path, routePath):
	# timetable/<date>
	# timetable/1

	path = path.split("/")
	routePath = routePath.split("/")

	args = []
	for i in range(len(routePath)):
		routePath[i] = routePath[i].replace("<path:", "!PATH")
		
		if "<" in routePath[i]:
			args.append(path[i])
		
		if "!PATH" in routePath[i]:
			args.append( '/'.join(path[i:]) )

	return args

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def route(path):
	if request.method == "OPTIONS":
		return addHeaders(Response(""))

	response = e404()

	route, routePath = findPath(path)
	if route != None:
		if request.method in route['method']:
			school = None
			response = route['function'](request, school, *parseArgs(path, routePath))
		else:
			response = e400()

	return addHeaders(response)

if __name__ == "__main__":
	startup()