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
	for i in routingMap.keys():
		path = re.sub('<.*?>', '', i).replace("//", "/")
		print(path)
		if i in path:
			if path != "" and i == "":
				continue
			#return routingMap[i]
	
	return None

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def route(path):
	if request.method == "OPTIONS":
		return addHeaders(Response(""))

	response = e404()

	route = findPath(path)
	if route != None:
		if request.method in route['method']:
			response = route['function'](request)
		else:
			response = e400()

	return addHeaders(response)

app.run(host = "0.0.0.0", debug = True)