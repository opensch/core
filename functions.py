from flask import Response

import classes, hashlib, binascii, time, json
import datetime, base64
import os

from config import Config

def e400():
	response = Response("Bad request", status = 400)
	return response


def e403():
	response = Response("Not allowed", status = 403)
	return response


def e404():
	response = Response("Not found", status = 404)
	return response

def e405():
	response = Response("Method not allowed", status = 405)
	return response


def stringToBool(string):
	string = str(string)

	if string == "0" or string.lower() == "false":
		return False
	if string == "1" or string.lower() == "true":
		return True
	raise ValueError("invalid literal for stringToBool()")

def mainPage(request):
    return Response("Hello to openSchool!")


def timetable(date, request):
	if request.method == 'POST':
		return e405()

	if request.method == 'OPTIONS':
		response = Response("")
		return response

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
	return response


def getIDbyToken(token):
	# Check if access token exists

	if( os.path.exists( "tokens/access/"+token ) ):
		with open( "tokens/access/"+token, "r" ) as f:
			j = json.loads( f.read() )
			if time.time() > j['expires']:
				return -1
			return j['uid']

	return -1


def findProfileByToken(token):
	# Insert a proper mechanism for identifying schools here!

	uid = getIDbyToken(token)

	if uid == -1:
		return None

	return classes.User.findById(school, uid)


def auth(request):
	# Insert a proper mechanism for identifying schools here!

	if request.method == 'OPTIONS':
		response = Response("")
		return response

	args = request.form

	if 'login' in args and 'password' in args and 'clientID' in args:
		# Login and password in request, so we can try to auth user.

		if args['clientID'] != Config().clientID:
			return e403()

		user = classes.User.findByLogin(school, args['login'])

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
				return response

		return e403()

	return e400()


def token_handler(request):
	if request.method == "OPTIONS":
		response = Response("")
		return response

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
	return response


def whoami(request):
	if request.method == 'OPTIONS':
		response = Response("")
		return response

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile != None:
		profile.password = ""
		response = Response(json.dumps(profile.toJSON()), status = 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		return e403()


def notifications_handler(request):
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

	return response
	

def passwd(request):
	if request.method == 'GET':
		return e405()
	elif request.method == 'OPTIONS':
		response = Response("")
		return response

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
			return response
		else:
			return e403()
	else:
		return e400()
		

def homework_handler(request, date, lesson):
	# Insert a proper mechanism for identifying schools here!

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if request.method == "GET":
		date = datetime.datetime.strptime(date, '%d.%m.%Y')

		if lesson != 'all':
			c = classes.HomeworkObject.retrieveHomework(school, profile, date, int(lesson))
		else:
			c = classes.HomeworkObject.find(school, user_uid = profile.uid, lessonDate = date)

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

		c = classes.HomeworkObject.retrieveHomework(school, profile, date, int(lesson))
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

	return response


def getTime(request):
	if request.method == 'OPTIONS':
		response = Response("")
		return response

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


def getTimes(request):
	if request.method == 'OPTIONS':
		response = Response("")
		return response

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

	return ret
	

def addToken(request):
	if request.method == 'GET':
		return e405()

	if request.method == 'OPTIONS':
		response = Response("")
		return response

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
		return response
	else:
		return e400()


def timetableToday(request):
	return timetable(datetime.datetime.now(), request)


def timetableDate(request, date):
	date = datetime.datetime.strptime(date, '%d.%m.%Y')
	return timetable(date, request)


def lesson(request):
	# Insert a proper mechanism for identifying schools here!

	if request.method == 'POST':
		return e405()

	if request.method == 'OPTIONS':
		response = Response("")
		return response

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	args = request.args

	if 'id' in args:
		lessonID = int(args['id'])

		foundLessonID = classes.Lesson.findById(school, lessonID)
		if(foundLessonID == None):
			response = Response(json.dumps({}), status = 200)
			response.headers['Content-Type'] = 'application/json'
			return response

		response = Response(json.dumps(foundLessonID.toJSON()), status = 200)
		return response
	
	return e400()


def cabinet(request):
	# Insert a proper mechanism for identifying schools here!

	if request.method == 'GET':
		return e405()

	if request.method == 'OPTIONS':
		response = Response("")
		return response

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	args = request.form

	if 'floor' in args:
		floorNumber = int(args['floor'])

		foundCabinets = classes.Cabinet.findByFloor(school, floorNumber)
		convertedCabinets = []

		for cabinet in foundCabinets:
			if cabinet == None:
				convertedCabinets.append({})
			else:
				convertedCabinets.append(cabinet.toJSON())

		response = Response(json.dumps(convertedCabinets), status = 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	elif 'number' in args:
		classNumber = int(args['number'])

		foundCabinet = classes.Cabinet.findByNumber(school, classNumber)

		if foundCabinet == None:
			response = Response(json.dumps({}), status = 200)
			response.headers['Content-Type'] = 'application/json'
			return response

		response = Response(json.dumps(foundCabinet.toJSON()), status = 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	
	return e400()


def cdn(request, data):
	if request.method == 'OPTIONS':
		response = Response("")
		return response

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	# If the user sends an encoded path, the built-in Flask
	# handlers don't follow the path. And so a user can access
	# any file on the server. So we clean up the path here.
	sanitized_path = ['cdn']
	data = data.replace("%2F", "/")

	for directory in data.split("/"):
		if directory == ".." and len(sanitized_path) > 1:
			del sanitized_path[-1]
		elif directory == ".." and len(sanitized_path) == 1:
			return e404()
		elif directory == "." or directory == '':
			pass
		else:
			sanitized_path.append(directory)
	
	sanitized_path = "/".join(sanitized_path)
	
	if not os.path.exists(sanitized_path):
		return "Not Found", 404
	if os.path.isdir(sanitized_path):
		return "Not Found", 404
	
	fileExt = sanitized_path.split(".")[1]
	
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

	response = make_response(send_file(sanitized_path))
	response.headers['Content-Type'] = mime
	return response

def getClasses(request):
	if request.method == 'OPTIONS':
		response = Response("")
		return response

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return response

	timetable = classes.createMongo().timetable

	class_numbers = timetable.distinct("classNumber")
	class_letters = timetable.distinct("classLetter")

	classes = []

	for class_number in class_numbers:
		for classLetter in class_letters:
			classes.append({"classNumber": classNumber, "classLetter": classLetter})

	response = Response(json.dumps(classes), status = 200)
	response.headers['Content-Type'] = 'application/json'
	return response

def getClassTimetable(request):
	# Insert a proper mechanism for identifying schools here!

	if request.method == 'OPTIONS':
		response = Response("")
		return response

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return response

	classNumber = request.args.get("classNumber")
	classLetter = request.args.get("classLetter")

	if classNumber == None or classLetter == None:
		return e400()

	timetable_request = {
		"classNumber": int(classNumber),
		"classLetter": classLetter
	}

	timetable = school.database.timetable
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
					lesson = classes.Lesson.findById(school, int(z.replace("I", "")))
					tmp.append(lesson.toJSON())
			else:
				lesson = classes.Lesson.findById(school, int(x.replace("A", "").replace("I", "")))
				tmp.append(lesson.toJSON())
			final[i].append(tmp)
			
	response = Response(json.dumps(final), status = 200)
	response.headers['Content-Type'] = 'application/json'
	return response


def createReplacement (request):
	if request.method == 'OPTIONS':
		response = Response("")
		return response
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return response
	
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

	return response


def editReplacement (request):
	if request.method == 'OPTIONS':
		response = Response("")
		return response
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return response
	
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
	
	return response

def getReplacements():
    return "who am i? why do i exist?"

def deleteReplacement (request):
	if request.method == 'OPTIONS':
		response = Response("")
		return response
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return response

	request_data = request.get_json()
	
	date = request_data["date"] 
	date = datetime.datetime.strptime(date, '%d.%m.%Y')
	
	position = request_data["position"] 
	class_number = request_data["classNumber"] 
	class_letter = request_data["classLetter"]
	
	classes.Replacement.delete(date, position, class_number, class_letter)  
	
	response = Response('', status = 200)
	return response


def createNews(request):
	if request.method == 'OPTIONS':
		response = Response("")
		return response
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return response

	request_data = request.get_json()

	title = request_data ["title"]
	markdown_text = request_data ["data"]
	is_important = request_data ["important"]

	news = classes.News.create(title, markdown_text, is_important)

	if news != None:
		json_news = json.dumps(news.toJSON())
		response = Response(json_news, 200)
	else:
		response = Response("", 400)

	return response


def editNews(request):
	if request.method == 'OPTIONS':
		response = Response("")
		return response
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return response

	request_data = request.get_json()
	
	title = request_data ["title"]
	new_data = request_data ["data"]
	
	news = classes.News.search(title)

	if news == None:
		response = Response("", 404)
	else:
		news.edit(new_data)
		response = Response("", 200)

	return response


def deleteNews(request):
	if request.method == 'OPTIONS':
		response = Response("")
		return response
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		response = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		return response

	request_data = request.get_json()
	
	title = request_data["title"]
	news = classes.News.search(title)

	if news == None:
		response = Response("", 404)
	else:
		news.delete()
		response = Response("", 410)

	return response


if __name__ == "__main__":
	startup()
