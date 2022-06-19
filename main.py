import os
if os.getenv("KUBERNETES") == "1":
	import kubernetesConfig

from flask import Flask, request, Response, make_response, send_file
import classes, hashlib, binascii, time, json
import datetime, base64

from config import Config

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


def add_cors_headers(response: Response):
	"""
	Cross-origin resource sharing sometimes plays bad with
	openSchool requests. As a ducktape solution, we allow
	accessing the server from any domain. 

	This fucntion add the CORS headers to the finallized response.
	"""
	
	response.headers['Access-Control-Allow-Origin'] = '*'
	response.headers['Access-Control-Allow-Headers'] = '*'
	response.headers['Access-Control-Allow-Methods'] = '*'	

	return response


def e403():
	response = Response("not allowed", status = 403)
	return add_cors_headers(response)


def e405():
	response = Response("method not allowed", status = 405)
	return add_cors_headers(response)


def e400():
	response = Response("bad request", status = 400)
	return add_cors_headers(response)


def stringToBool(string):
	string = str(string)

	if string == "0" or string.lower() == "false":
		return False
	if string == "1" or string.lower() == "true":
		return True
	raise ValueError("invalid literal for stringToBool()")


def timetable(date, request):
	if request.method == 'POST':
		return e405()

	if request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	timetable = classes.Timetable.createTimetable(profile, date)
	if timetable == None:
		timetable = classes.Timetable()

	response = Response(json.dumps(timetable.toJSON()), status = 200)
	response.headers['Content-Type'] = 'application/json'
	return add_cors_headers(response)


def getIDbyToken(token):
	# Check if access token exists

	if( os.path.exists( "tokens/access/"+token ) ):
		with open( "tokens/access/"+token, "response" ) as f:
			j = json.loads( f.read() )
			if time.time() > j['expires']:
				return -1
			return j['uid']

	return -1


def findProfileByToken(token):
	uid = getIDbyToken(token)

	if uid == -1:
		return None

	return classes.User.findById(uid)


@app.route("/oauth/auth", methods = [ 'POST',  'OPTIONS' ])
def auth():
	if request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)

	args = request.form

	if 'login' in args and 'password' in args and 'clientID' in args:
		# Login and password in request, so we can try to auth user.

		if args['clientID'] != Config().clientID:
			return e403()

		user = classes.User.findByLogin(args['login'])

		if user == None:
			return e403()

		if args['login'] == user.login:
			h = hashlib.sha512(args['password'].encode())
			if user.password == h.hexdigest():
				code = binascii.b2a_hex(os.urandom(15)).decode()
				with open( 'codes/'+code, 'w' ) as f:
					data = {}
					data['uid'] = user.uid
					data['time'] = time.time() + 300
					f.write( json.dumps(data) )
				
				response = Response(code, status = 200)
				return add_cors_headers(response)

		return e403()

	return e400()


@app.route("/oauth/token", methods = [ "POST", "OPTIONS" ])
def token_handler():
	if request.method == "OPTIONS":
		response = Response("")
		return add_cors_headers(response)

	arguments = request.form
	
	if "clientSecret" not in arguments:
		return e400()
	elif arguments["clientSecret"] != Config().clientSecret:
		return e403()

	if "refreshToken" in arguments:
		directory = "tokens/refresh/" + arguments["refreshToken"]
		
		if os.path.exists(directory) != True:
			return e403()
		with open(directory) as file:
			token_data = json.loads(file.read())
		
		if os.path.exists("tokens/access/" + token_data["lastToken"]):
			os.remove("tokens/access/" + token_data["lastToken"])
		
		refresh_hash = arguments["refreshToken"]
	
	elif "code" in arguments:
		directory = "codes/" + arguments["code"]

		if os.path.exists(directory) != True:
			return e403()
		with open(directory) as file:
			token_data = json.loads(file.read())

		if token_data["time"] < time.time():
			os.remove(directory + token)
			return e403()
		
		refresh_hash = binascii.b2a_hex(os.urandom(32)).decode()

	else:
		return e400()

	access_hash = binascii.b2a_hex(os.urandom(32)).decode()	
	
	if Config().mode == "production":
		expiry_time = time.time() + 2592000
	else:
		expiry_time = time.time() + 1800
	
	access_data = {"uid": token_data["uid"], "expires": expiry_time}
	refresh_data = {"uid": token_data["uid"], "lastToken": access_hash}

	with open("tokens/access/" + access_hash, "w") as file:
		file.write(json.dumps(access_data))
	with open("tokens/refresh/" + refresh_hash, "w") as file:
		file.write(json.dumps(refresh_data))

	response = {
		"accessToken": access_hash,
		"refreshToken": refresh_hash,
		"expiresIn": expiry_time
	}

	response = Response(json.dumps(response), status = 200)
	response.headers["Content-Type"] = "application/json"
	return add_cors_headers(response)


@app.route("/user/whoami", methods = [ 'POST', 'GET', 'OPTIONS' ])
def whoami():
	if request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile != None:
		profile.password = ""
		response = Response(json.dumps(profile.toJSON()), status = 200)
		response.headers['Content-Type'] = 'application/json'
		return add_cors_headers(response)
	else:
		return e403()


@app.route("/user/notifications", methods = [ 'GET', 'POST', 'OPTIONS' ])
def notifications_handler():
	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if request.method == "GET":
		response = Response( json.dumps(profile.notifParams), status = 200)
		response.headers['Content-Type'] = "application/json"
	
	elif request.method == "POST":
		args = request.form
		
		print([i for i in args])

		found = 0

		try:
			if '10min' in args:
				found = 1
				profile.notifParams['10min'] = stringToBool(args['10min'])
			if 'homework' in args:
				found = 1
				profile.notifParams['homework'] = stringToBool(args['homework'])
			if 'homeworkTime' in args:
				found = 1
				profile.notifParams['homeworkTime'] = int(args['homeworkTime'])
			if 'replacements' in args:
				found = 1
				profile.notifParams['replacements'] = stringToBool(args['replacements'])
		except Exception:
			pass

		if found == 0:
			return e400()

		profile.editUser(profile)

		response = Response(json.dumps({"status": "ok", "c": profile.notifParams}), status = 200)
		response.headers['Content-Type'] = 'application/json'
	
	elif request.method == 'OPTIONS':
		response = Response("")

	return add_cors_headers(response)
	

@app.route("/user/passwd", methods = [ 'POST', 'GET', 'OPTIONS' ])
def passwd():
	if request.method == 'GET':
		return e405()
	elif request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	args = request.form

	if 'old' in args and 'new' in args:
		h = hashlib.sha512(args['old'].encode())
		if profile.password == h.hexdigest():
			h = hashlib.sha512(args['new'].encode())
			nU = classes.User()
			nU.password = h.hexdigest

			profile.editUser(nU)

			response = Response(json.dumps({"status": "ok"}), status = 200)
			return add_cors_headers(response)
		else:
			return e403()
	else:
		return e400()
		

@app.route("/homework/<date>/<lesson>", methods = [ 'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS' ])
def homework_handler(date, lesson):
	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if request.method == "GET":
		date = datetime.datetime.strptime(date, '%d.%m.%Y')

		if lesson != 'all':
			c = classes.HomeworkObject.retrieveHomework(profile, date, int(lesson))
		else:
			c = classes.HomeworkObject.find(user_uid = profile.uid, lessonDate = date)

		n = []
		for i in c:
			n.append(i.toJSON())

		response = Response(json.dumps(n), status = 200)
		response.headers['Content-Type'] = 'application/json'
		
	elif request.method == "POST":
		args = request.form
		nA = ['oldContentHash', 'contentN']
		
		if "oldContentHash" not in args:
			return e400()
		if "contentN" not in args:
			return e400()

		token = request.headers['Authorization']
		profile = findProfileByToken(token)
		if profile == None:
			return e403()

		date = datetime.datetime.strptime(date, '%d.%m.%Y')

		c = classes.HomeworkObject.retrieveHomework(profile, date, int(lesson))
		h = None

		for i in c:
			m = i.data.encode()
			if base64.b64encode(m).decode() == args['oldContentHash']:
				h = i

		nH = classes.HomeworkObject()
		nH.user_uid = profile.uid
		nH.lessonDate = date
		nH.lessonID = int(lesson)
		nH.data = args['contentN']

		if h != None:
			print("Homework not found")
			h.editHomework(nH)
			response = Response("", status = 200)

		return e400()
	
	elif request.method == "PUT":
		args = request.form

		if "content" not in args:
			return e400()

		token = request.headers['Authorization']
		profile = findProfileByToken(token)
		if profile == None:
			return e403()

		date = datetime.datetime.strptime(date, '%d.%m.%Y')

		n = classes.HomeworkObject.createHomework(profile, date, int(lesson), args['content'])

		response = Response("", status = 200)

	elif request.method == "DELETE":
		args = request.form
		
		if "contentHash" not in args:
			return e400()

		token = request.headers['Authorization']
		profile = findProfileByToken(token)
		if profile == None:
			return e403()

		date = datetime.datetime.strptime(args['date'], '%d.%m.%Y')

		c = classes.HomeworkObject.retrieveHomework(profile, date, int(args['lesson']))
		h = None

		for i in c:
			h = i.data.encode()
			if base64.b64encode(h).decode() == args['contentHash']:
				h = i

		h.deleteHomework()

		response = Response("", status = 200)
		
	elif request.method == "OPTIONS":
		response = Response("")

	return add_cors_headers(response)


@app.route("/time", methods = [ 'GET', 'OPTIONS' ])
def getTime():
	if request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	number = request.args.get("number")
	if number == None:
		return e400()

	with open("time.json") as timeDataFile:
		timeData = json.loads(timeDataFile.read())

	timeObj = timeData['default']
	if str(profile.classNumber) in timeData:
		timeObj = timeData[str(profile.classNumber)]
	print(timeObj)

	try:
		ret = timeObj[int(number)]
	except Exception:
		return e400()

	return ret


@app.route("/times", methods = [ 'GET', 'OPTIONS' ])
def getTimes():
	if request.method == 'OPTIONS':
		response = Response("")
		response.headers['Access-Control-Allow-Origin'] = "*"
		
		
		return add_cors_headers(response)

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	with open("time.json") as timeDataFile:
		timeData = json.loads(timeDataFile.read())

	timeObj = timeData['default']
	if str(profile.classNumber) in timeData:
		timeObj = timeData[str(profile.classNumber)]
	print(timeObj)

	try:
		ret = Response(json.dumps(timeObj), status = 200)
		ret.headers['Content-Type'] = 'application/json'
	except Exception:
		return e400()

	return add_cors_headers(ret)
	

@app.route("/newfirebase", methods = [ 'POST', 'GET', 'OPTIONS' ])
def addToken():
	if request.method == 'GET':
		return e405()

	if request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	args = request.form

	if 'token' in args:
		if args['token'] not in profile.tokens:
			profile.tokens.append( args['token'] )
			profile.editUser(profile)

		response = Response(json.dumps({"status": "ok"}), status = 200)
		response.headers['Content-Type'] = 'application/json'
		return add_cors_headers(response)
	else:
		return e400()


@app.route("/timetable", methods = [ 'POST', 'GET', 'OPTIONS' ])
def timetableToday():
	return timetable(datetime.datetime.now(), request)


@app.route("/timetable/<date>", methods = [ 'POST', 'GET', 'OPTIONS' ])
def timetableDate(date):
	date = datetime.datetime.strptime(date, '%d.%m.%Y')
	return timetable(date, request)


@app.route("/lesson", methods = ['POST', 'GET', 'OPTIONS'])
def lesson():
	if request.method == 'POST':
		return e405()

	if request.method == 'OPTIONS':
		response = Response("")
		response.headers['Access-Control-Allow-Origin'] = "*"
		return add_cors_headers(response)

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	args = request.args

	if 'id' in args:
		lessonID = int(args['id'])

		foundLessonID = classes.Lesson.findById(lessonID)
		if(foundLessonID == None):
			response = Response(json.dumps({}), status = 200)
			response.headers['Content-Type'] = 'application/json'

			return add_cors_headers(response)

		response = Response(json.dumps(foundLessonID.toJSON()), status = 200)
		return add_cors_headers(response)
	
	return e400()


@app.route("/cabinet", methods = ['POST', 'GET', 'OPTIONS'])
def cabinet():
	if request.method == 'POST':
		return e405()

	if request.method == 'OPTIONS':
		response = Response("")
		response.headers['Access-Control-Allow-Origin'] = "*"
		return add_cors_headers(response)

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	args = request.form

	if 'floor' in args:
		floorNumber = int(args['floor'])

		foundCabinets = classes.Cabinet.findByFloor(floorNumber)
		convertedCabinets = []

		for cabinet in foundCabinets:
			if cabinet == None:
				convertedCabinets.append({})
			else:
				convertedCabinets.append(cabinet.toJSON())

		response = Response(json.dumps(convertedCabinets), status = 200)
		response.headers['Content-Type'] = 'application/json'
		return add_cors_headers(response)

	elif 'number' in args:
		classNumber = int(args['number'])

		foundCabinet = classes.Cabinet.findByNumber(classNumber)

		if foundCabinet == None:
			response = Response(json.dumps({}), status = 200)
			response.headers['Content-Type'] = 'application/json'
			return add_cors_headers(response)

		response = Response(json.dumps(foundCabinet.toJSON()), status = 200)
		response.headers['Content-Type'] = 'application/json'
		return add_cors_headers(response)
	
	return e400()


@app.route("/cdn/<path:data>", methods = [ 'GET', 'OPTIONS' ])
def cdn(data):
	if request.method == 'OPTIONS':
		response = Response("")
		response.headers['Access-Control-Allow-Origin'] = "*"
		return add_cors_headers(response)

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	urlParts = data.split("/")
	urlRoot = urlParts[0]
	serverDir = "cdn/"+urlRoot

	for x in urlParts:
		if x != urlRoot:
			if os.path.isdir(serverDir+"/"+x) or os.path.exists(serverDir+"/"+x):
				serverDir = serverDir+"/"+x
			else:
				return "Not Found", 404

	if os.path.isdir(serverDir) or os.path.exists(serverDir):
		pass
	else:
		return "Not Found", 404
	
	fileExt = serverDir.split(".")[1]
	
	mime = "plain/text"

	if fileExt == "json":
		mime = "application/json"
	if fileExt == "pdf":
		mime = "application/pdf"
	if fileExt == "png":
		mime = "image/png"
	if fileExt == "gif":
		mime = "image/gif"
	if fileExt == ".html" or fileExt == ".htm":
		mime = "text/html"
	if fileExt == ".jpeg" or fileExt == ".jpg":
		mime = "image/jpeg"

	response = make_response(send_file(serverDir))
	response.headers['Content-Type'] = mime
	return add_cors_headers(response)

@app.route("/privAPI/getClasses", methods = [ 'GET', 'OPTIONS' ])
def getClasses():
	if request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return add_cors_headers(response)

	timetable = classes.createMongo().timetable

	class_numbers = timetable.distinct("classNumber")
	class_letters = timetable.distinct("classLetter")

	classes = []

	for class_number in class_numbers:
		for classLetter in class_letters:
			classes.append({"classNumber": classNumber, "classLetter": classLetter})

	response = Response(json.dumps(classes), status = 200)
	response.headers['Content-Type'] = 'application/json'
	return add_cors_headers(response)

@app.route("/privAPI/getClassTimetable", methods = [ 'GET', 'OPTIONS' ])
def getClassTimetable():
	if request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return add_cors_headers(response)

	classNumber = request.args.get("classNumber")
	classLetter = request.args.get("classLetter")

	if classNumber == None or classLetter == None:
		return e400()

	timetable_request = {
		"classNumber": int(classNumber),
		"classLetter": classLetter
	}

	timetable = classes.createMongo().timetable
	timetable = timetable.find_one(timetable_request)

	if timetable: timetable = timetable ["lessons"]
	else: return None

	final = {
		"0": [],
		"1": [],
		"2": [],
		"3": [],
		"4": []
	}

	for i in timetable:
		day = timetable[i]
		tmp = []
		for x in day:
			tmp = []
			if x == "-":
				tmp.append("-")
			elif "," in x:
				n = x.split(",")
				for z in n:
					lesson = classes.Lesson.findById(int(z.replace("I", "")))
					tmp.append(lesson.toJSON())
			else:
				lesson = classes.Lesson.findById(int(x.replace("A", "").replace("I", "")))
				tmp.append(lesson.toJSON())
			final[i].append(tmp)
			
	response = Response(json.dumps(final), status = 200)
	response.headers['Content-Type'] = 'application/json'
	return add_cors_headers(response)


@app.route("/privAPI/createReplacement", methods = [ "POST", "OPTIONS" ])
def createReplacement ():
	if request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return add_cors_headers(response)
	
	request_data = request.get_json()
	
	date = request_data["date"] 
	date = datetime.datetime.strptime(date, '%d.%m.%Y')
	
	position = request_data["position"] 
	class_number = request_data["classNumber"] 
	class_letter = request_data["classLetter"]

	old_lesson = request_data["oldLesson"] 
	old_lesson = classes.Lesson.fromJSON(old_lesson)

	new_lesson = request_data["newLesson"] 
	new_lesson = classes.Lesson.fromJSON(new_lesson)

	replacement = classes.Replacement.create(date, position, class_number, class_letter, old_lesson, new_lesson) 

	if replacement:
		response = Response('', status = 200)
	else:
		response = Response('', status = 400)

	return add_cors_headers(response)


@app.route("/privAPI/editReplacement", methods = [ "POST", "OPTIONS" ])
def editReplacement ():
	if request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return add_cors_headers(response)
	
	request_data = request.get_json()
	
	date = request_data["date"] 
	date = datetime.datetime.strptime(date, '%d.%m.%Y')
	
	position = request_data["position"] 
	class_number = request_data["classNumber"] 
	class_letter = request_data["classLetter"]

	old_lesson = request_data["oldLesson"] 
	old_lesson = classes.Lesson.fromJSON(old_lesson)

	new_lesson = request_data["newLesson"] 
	new_lesson = classes.Lesson.fromJSON(new_lesson)

	replacement = classes.Replacement.edit(date, position, class_number, class_letter, old_lesson, new_lesson)
	
	if replacement:
		response = Response('', status = 200)
	else:
		response = Response('', status = 400)
	
	return add_cors_headers(response)


@app.route("/privAPI/deleteReplacement", methods = [ "POST", "OPTIONS" ])  
def deleteReplacement ():
	if request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return add_cors_headers(response)

	request_data = request.get_json()
	
	date = request_data["date"] 
	date = datetime.datetime.strptime(date, '%d.%m.%Y')
	
	position = request_data["position"] 
	class_number = request_data["classNumber"] 
	class_letter = request_data["classLetter"]
	
	classes.Replacement.delete(date, position, class_number, class_letter)  
	
	response = Response('', status = 200)
	return add_cors_headers(response)


@app.route("/privAPI/createNews", methods = ["POST", "OPTIONS"])
def createNews():
	if request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return add_cors_headers(response)

	request_data = request.get_json()

	title = request_data ["title"]
	markdown_text = reqeuest_data ["data"]
	is_important = request_data ["important"]

	news = classes.News.create(title, markdown_text, is_important)

	if news != None:
		json_news = json.dumps(news.toJSON())
		response = Response(json_news, 200)
	else:
		response = Response("", 400)

	return add_cors_headers(response)


@app.route("/privAPI/editNews", methods = ["POST", "OPTIONS"])
def editNews():
	if request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return add_cors_headers(response)

	request_data = request.get_json()
	
	title = reqeust_data ["title"]
	new_data = request_data ["data"]
	
	news = classes.News.search(title)

	if news == None:
		response = Response("", 404)
	else:
		news.edit(new_data)
		response = Response("", 200)

	return add_cors_headers(response)


@app.route("/privAPI/deleteNews", methods = ["POST", "OPTIONS"])
def deleteNews():
	if request.method == 'OPTIONS':
		response = Response("")
		return add_cors_headers(response)
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return add_cors_headers(response)

	request_data = request.get_json()
	
	title = reqeust_data ["title"]
	news = classes.News.search(title)

	if news == None:
		response = Response("", 404)
	else:
		news.delete()
		response = Response("", 410)

	return add_cors_headers(response)


@app.route("/")
def main():
	response = Response("Not Found", status = 404)
	return add_cors_headers(response)


if __name__ == "__main__":
	startup()
