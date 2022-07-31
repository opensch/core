import os, re, json, tldextract

from flask import Flask, request, Response 

from config import Config
from classes import School
from server.routes import routingMap
from server.helpers import e400, e404

if os.getenv("KUBERNETES") == "1":
	import kubernetesConfig

app = Flask(__name__)

def startup ():
	"""
	This is the initialization function. It is run first to prepare
	the environment before starting up the Flask application, like folder
	creation, configuration file checking, etc.
	"""
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

	if len(path) == 0:
		if 'homePage' in routingMap:
			return routingMap["homePage"]

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

	return None, None


def parseArgs(path, routePath):
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

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods = HTTP_METHODS)
def route(path):
	if request.method == "OPTIONS":
		return addHeaders(Response(""))

	response = e404()

	if path == "favicon.ico":
		return "", 404

	route, routePath = findPath(path)

	if route == None:
		schoolName = path.split("/")[0]

		path = path.split("/")
		del path[0]
		path = '/'.join(path)

		route, routePath = findPath(path)
	else:
		schoolName = tldextract.extract(request.url).subdomain
	
	if schoolName == "":
		return "No school specified", 400
	else:
		school = School.with_domain(schoolName)
		if school == False:
			return "School not found", 404

	if route != None:
		if request.method in route['method']:
			response = route['function'](request, school, *parseArgs(path, routePath))
		else:
			response = e405()

	return addHeaders(response)

if __name__ == "__main__":
	startup()
