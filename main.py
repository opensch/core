from flask import Flask, request, Response, make_response, send_file
import classes, hashlib, os, binascii, time, json
import datetime, base64

from config import Config


app = Flask(__name__)

if os.path.isdir("tokens/access") != True:
	os.mkdir("tokens/access")

if os.path.isdir("tokens/refresh") != True:
	os.mkdir("tokens/refresh")

def e403():
	r = Response("not allowed", status = 403)
	r.headers['access-control-allow-origin'] = '*'
	r.headers['Access-Control-Allow-Headers'] = '*'
	r.headers['Access-Control-Allow-Methods'] = '*'

	return r

def e405():
	r = Response("method not allowed", status = 405)
	r.headers['access-control-allow-origin'] = '*'
	r.headers['Access-Control-Allow-Headers'] = '*'
	r.headers['Access-Control-Allow-Methods'] = '*'

	return r

def e400():
	r = Response("bad request", status = 400)
	r.headers['access-control-allow-origin'] = '*'
	r.headers['Access-Control-Allow-Headers'] = '*'
	r.headers['Access-Control-Allow-Methods'] = '*'

	return r

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
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	timetable = classes.Timetable.createTimetable(profile, date)
	if timetable == None:
		timetable = classes.Timetable()

	r = Response(json.dumps(timetable.toJSON()), status = 200)
	r.headers['Content-Type'] = 'application/json'
	r.headers['Access-Control-Allow-Origin'] = '*'
	r.headers['Access-Control-Allow-Headers'] = '*'
	r.headers['Access-Control-Allow-Methods'] = '*'
	return r

@app.route("/getNotif", methods = [ 'GET', 'OPTIONS' ])
def getNotificationSettings():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	resp = Response( json.dumps(profile.notifParams), status = 200)
	resp.headers['Content-Type'] = "application/json"
	resp.headers['Access-Control-Allow-Origin'] = '*'
	resp.headers['Access-Control-Allow-Headers'] = '*'
	resp.headers['Access-Control-Allow-Methods'] = '*'

	return resp

@app.route("/time", methods = [ 'GET', 'OPTIONS' ])
def getTime():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

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
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

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
		ret.headers['Access-Control-Allow-Origin'] = '*'
		ret.headers['Access-Control-Allow-Headers'] = '*'
		ret.headers['Access-Control-Allow-Methods'] = '*'
	except Exception:
		return e400()

	return ret

@app.route("/setNotif", methods = [ 'GET', 'OPTIONS' ])
def setNotificationSettings():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	   
	args = request.args

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

	r = Response(json.dumps({"status": "ok", "c": profile.notifParams}), status = 200)
	r.headers['Content-Type'] = 'application/json'
	r.headers['Access-Control-Allow-Origin'] = '*'
	r.headers['Access-Control-Allow-Headers'] = '*'
	r.headers['Access-Control-Allow-Methods'] = '*'

	return r
	

@app.route("/newfirebase", methods = [ 'POST', 'GET', 'OPTIONS' ])
def addToken():
	if request.method == 'GET':
		return e405()

	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

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

		r = Response(json.dumps({"status": "ok"}), status = 200)
		r.headers['Content-Type'] = 'application/json'
		r.headers['Access-Control-Allow-Origin'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'

		return r
	else:
		return e400()

@app.route("/passwd", methods = [ 'POST', 'GET', 'OPTIONS' ])
def passwd():
	if request.method == 'GET':
		return e405()

	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

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

			r = Response(json.dumps({"status": "ok"}), status = 200)
			r.headers['Content-Type'] = 'application/json'
			r.headers['Access-Control-Allow-Origin'] = '*'
			r.headers['Access-Control-Allow-Headers'] = '*'
			r.headers['Access-Control-Allow-Methods'] = '*'

			return r
		else:
			return e403()
	else:
		return e400()

@app.route("/homework/<date>/<lesson>", methods = [ 'GET', 'OPTIONS' ])
def gHomework(date, lesson):
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	date = datetime.datetime.strptime(date, '%d.%m.%Y')


	if lesson != 'all':
		c = classes.HomeworkObject.retrieveHomework(profile, date, int(lesson))
	else:
		c = classes.HomeworkObject.find(user_uid = profile.uid, lessonDate = date)

	n = []
	for i in c:
		n.append(i.toJSON())

	r = Response(json.dumps(n), status = 200)
	r.headers['Content-Type'] = 'application/json'
	r.headers['Access-Control-Allow-Origin'] = '*'
	r.headers['Access-Control-Allow-Headers'] = '*'
	r.headers['Access-Control-Allow-Methods'] = '*'

	return r

@app.route("/editHomework", methods = [ 'POST', 'OPTIONS' ])
def editHomework():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

	if 'Authorization' not in request.headers:
		return e403()

	args = request.form
	nA = ['date', 'lesson', 'oldContentHash', 'dateN', 'lessonN', 'contentN']

	for x in nA:
		if x not in args:
			return e400()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	date = datetime.datetime.strptime(args['date'], '%d.%m.%Y')

	c = classes.HomeworkObject.retrieveHomework(profile, date, int(args['lesson']))
	h = None

	for i in c:
		m = i.data.encode()
		if base64.b64encode(m).decode() == args['oldContentHash']:
			h = i

	nH = classes.HomeworkObject()
	nH.user_uid = profile.uid
	nH.lessonDate = datetime.datetime.strptime(args['dateN'], '%d.%m.%Y')
	nH.lessonID = int(args['lessonN'])
	nH.data = args['contentN']

	if h != None:
		h.editHomework(nH)
		return '', 200
	return e400()
	
@app.route("/delHomework", methods = [ 'POST', 'OPTIONS' ])
def delHomework():
		if request.method == 'OPTIONS':
			r = Response("")
			r.headers['Access-Control-Allow-Origin'] = "*"
			r.headers['Access-Control-Allow-Headers'] = '*'
			r.headers['Access-Control-Allow-Methods'] = '*'
			return r

		if 'Authorization' not in request.headers:
				return e403()

		args = request.form
		nA = ['date', 'lesson', 'contentHash']

		for x in nA:
				if x not in args:
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

		return '', 200

@app.route('/appendHomework', methods = [ 'POST', 'OPTIONS' ])
def appendHomework():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

	if 'Authorization' not in request.headers:
		return e403()

	args = request.form
	nA = ['date', 'lesson', 'content']

	for x in nA:
		if x not in args:
			return e400()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	date = datetime.datetime.strptime(args['date'], '%d.%m.%Y')

	n = classes.HomeworkObject.createHomework(profile, date, int(args['lesson']), args['content'])

	return '', 200

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
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

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
			r = Response(json.dumps({}), status = 200)
			r.headers['Content-Type'] = 'application/json'
			r.headers['Access-Control-Allow-Origin'] = '*'
			r.headers['Access-Control-Allow-Headers'] = '*'
			r.headers['Access-Control-Allow-Methods'] = '*'
			return r

		r = Response(json.dumps(foundLessonID.toJSON()), status = 200)
		r.headers['Access-Control-Allow-Origin'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r
	return e400()

@app.route("/cabinet", methods = ['POST', 'GET', 'OPTIONS'])
def cabinet():
	if request.method == 'POST':
		return e405()

	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

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

		r = Response(json.dumps(convertedCabinets), status = 200)
		r.headers['Content-Type'] = 'application/json'
		r.headers['Access-Control-Allow-Origin'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

	elif 'number' in args:
		classNumber = int(args['number'])

		foundCabinet = classes.Cabinet.findByNumber(classNumber)

		if foundCabinet == None:
			r = Response(json.dumps({}), status = 200)
			r.headers['Content-Type'] = 'application/json'
			r.headers['Access-Control-Allow-Origin'] = '*'
			r.headers['Access-Control-Allow-Headers'] = '*'
			r.headers['Access-Control-Allow-Methods'] = '*'
			return r

		r = Response(json.dumps(foundCabinet.toJSON()), status = 200)
		r.headers['Content-Type'] = 'application/json'
		r.headers['Access-Control-Allow-Origin'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r
	return e400()

@app.route("/auth", methods = [ 'POST', 'GET', 'OPTIONS' ])
def auth():
	if request.method == 'GET':
		return e405()

	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

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
				r = Response(code, status = 200)
				r.headers['Content-Type'] = 'application/json'
				r.headers['Access-Control-Allow-Origin'] = '*'
				r.headers['Access-Control-Allow-Headers'] = '*'
				r.headers['Access-Control-Allow-Methods'] = '*'

				return r

		return e403()

	return e400()

@app.route("/exchange", methods = [ 'POST', 'GET', 'OPTIONS' ])
def exchange():
	if request.method == 'GET':
		return e405()

	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

	args = request.form
	resp = None

	if 'clientSecret' in args and 'code' in args:
		# Check if code exists.

		if os.path.exists( "codes/"+args['code'] ) != True:
			return e403()

		#OK! Code exists. Let's verify it's date and verify clientSecret

		if args['clientSecret'] != Config().clientSecret:
			return e403()

		with open( "codes/"+args['code'], "r" ) as f:
			j = json.loads( f.read() )
			if( j['time'] > time.time() ):
				# Code ok, so we can create access and refresh token.

				expiresDate = time.time() + 2592000
				if Config().mode == "development":
					#For development mode we'll use tokens that expires after 30 minutes.
					expiresDate = time.time() + 1800

				tokenHash = binascii.b2a_hex(os.urandom(32)).decode()
				refreshHash = binascii.b2a_hex(os.urandom(32)).decode()

				tokenData = { "uid": j['uid'], "expires": expiresDate}
				refreshData = { "uid": j['uid'], "lastToken": tokenHash}

				with open( "tokens/access/"+tokenHash, "w" ) as f:
					f.write( json.dumps(tokenData) )

				with open( "tokens/refresh/"+refreshHash, "w" ) as f:
					f.write( json.dumps(refreshData) )

				resp = {
					"accessToken": tokenHash,
					"refreshToken": refreshHash,
					"expiresIn": expiresDate
				}

		if resp != None:
			os.remove( "codes/"+args['code'] )				

			r = Response( json.dumps(resp), status = 200 )
			r.headers['Content-Type'] = 'application/json'
			r.headers['Access-Control-Allow-Origin'] = '*'
			r.headers['Access-Control-Allow-Headers'] = '*'
			r.headers['Access-Control-Allow-Methods'] = '*'
			return r
			
		return e403()

	return e400()

@app.route("/refresh", methods = [ 'POST', 'GET', 'OPTIONS' ])
def refresh():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

	if request.method == 'GET':
		return e405()

	args = request.form

	if 'clientSecret' in args and 'refreshToken' in args:
		# Check if token exists.

		if os.path.exists( "tokens/refresh/"+args['refreshToken'] ) != True:
			return e403()

		#OK! Token exists. Let's verify it's date and verify clientSecret

		if args['clientSecret'] != Config().clientSecret:
			return e403()
		
		with open( "tokens/refresh/"+args['refreshToken'], "r+" ) as f:
			j = json.loads( f.read() )
# We need to delete last token (to revoke it and to clean up folder with tokens)

			if os.path.exists( "tokens/access/" + j['lastToken'] ):
				print("del")
				os.remove("tokens/access/" + j['lastToken'] )
	
			expiresDate = time.time() + 2592000
			if Config().mode == "development":
				# For development mode we'll use tokens that expires after 30 minutes.
				expiresDate = time.time() + 1800
			
			tokenHash = binascii.b2a_hex(os.urandom(32)).decode()
			tokenData = { "uid": j['uid'], "expires": expiresDate}
				
			with open( "tokens/access/"+tokenHash, "w" ) as x:
				x.write( json.dumps(tokenData) )

			resp = {
				"accessToken": tokenHash,
				"refreshToken": args['refreshToken'],
				"expiresIn": expiresDate
			}

			f.seek(0)

			j['lastToken'] = tokenHash
			f.write( json.dumps(j) )

			r = Response( json.dumps(resp), status = 200 )
			r.headers['Content-Type'] = 'application/json'
			r.headers['Access-Control-Allow-Origin'] = '*'
			r.headers['Access-Control-Allow-Headers'] = '*'
			r.headers['Access-Control-Allow-Methods'] = '*'
			return r

	return e400()

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
	uid = getIDbyToken(token)

	if uid == -1:
		return None

	return classes.User.findById(uid)

@app.route("/whoami", methods = [ 'POST', 'GET', 'OPTIONS' ])
def whoami():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile != None:
		profile.password = ""
		r = Response(json.dumps(profile.toJSON()), status = 200)
		r.headers['Content-Type'] = 'application/json'
		r.headers['Access-Control-Allow-Origin'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		return r
	else:
		return e403()

@app.route("/cdn/<path:data>", methods = [ 'GET', 'OPTIONS' ])
def cdn(data):
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

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
	response.headers['Access-Control-Allow-Origin'] = '*'
	response.headers['Access-Control-Allow-Headers'] = '*'
	response.headers['Access-Control-Allow-Methods'] = '*'
	return response

@app.route("/privAPI/getClasses", methods = [ 'GET', 'OPTIONS' ])
def getClasses():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	if 'role' not in profile.flags or profile.flags['role'] == 0:
		r = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		r.headers['access-control-allow-origin'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
	
		return r

	timetable = classes.createMongo().timetable

	class_numbers = timetable.distinct("classNumber")
	class_letters = timetable.distinct("classLetter")

	classes = []

	for class_number in class_numbers:
		for classLetter in class_letters:
			classes.append({"classNumber": classNumber, "classLetter": classLetter})

	r = Response(json.dumps(classes), status = 200)
	r.headers['Content-Type'] = 'application/json'
	r.headers['Access-Control-Allow-Origin'] = "*"
	r.headers['Access-Control-Allow-Headers'] = '*'
	r.headers['Access-Control-Allow-Methods'] = '*'

	return r

@app.route("/privAPI/getClassTimetable", methods = [ 'GET', 'OPTIONS' ])
def getClassTimetable():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r

	if 'Authorization' not in request.headers:
		return e403()

	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()

	if 'role' not in profile.flags or profile.flags['role'] == 0:
		r = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		r.headers['access-control-allow-origin'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
	
		return r

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
			
	r = Response(json.dumps(final), status = 200)
	r.headers['Content-Type'] = 'application/json'
	r.headers['Access-Control-Allow-Origin'] = "*"
	r.headers['Access-Control-Allow-Headers'] = '*'
	r.headers['Access-Control-Allow-Methods'] = '*'

	return r


@app.route("/privAPI/createReplacement", methods = [ "POST", "OPTIONS" ])
def createReplacement ():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		r = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		r.headers['access-control-allow-origin'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'

		return r
	
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
	
	response.headers['Access-Control-Allow-Origin'] = "*"
	response.headers['Access-Control-Allow-Headers'] = '*'
	response.headers['Access-Control-Allow-Methods'] = '*'

	return response


@app.route("/privAPI/editReplacement", methods = [ "POST", "OPTIONS" ])
def editReplacement ():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		r = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		r.headers['access-control-allow-origin'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
	
		return r
	
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
	
	response.headers['Access-Control-Allow-Origin'] = "*"
	response.headers['Access-Control-Allow-Headers'] = '*'
	response.headers['Access-Control-Allow-Methods'] = '*'
	
	return response


@app.route("/privAPI/deleteReplacement", methods = [ "POST", "OPTIONS" ])  
def deleteReplacement ():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		r = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		r.headers['access-control-allow-origin'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
	
		return r

	request_data = request.get_json()
	
	date = request_data["date"] 
	date = datetime.datetime.strptime(date, '%d.%m.%Y')
	
	position = request_data["position"] 
	class_number = request_data["classNumber"] 
	class_letter = request_data["classLetter"]
	
	classes.Replacement.delete(date, position, class_number, class_letter)  
	
	response = Response('', status = 200)

	response.headers['Access-Control-Allow-Origin'] = "*"
	response.headers['Access-Control-Allow-Headers'] = '*'
	response.headers['Access-Control-Allow-Methods'] = '*'
	
	return response


@app.route("privAPI/createNews", methods = ["POST", "OPTIONS"])
def createNews ():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		r = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		r.headers['access-control-allow-origin'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
	
		return r

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

	response.headers['Access-Control-Allow-Origin'] = "*"
	response.headers['Access-Control-Allow-Headers'] = '*'
	response.headers['Access-Control-Allow-Methods'] = '*'

	return response


@app.route("privAPI/editNews", methods = ["POST", "OPTIONS"])
def editNews():
	if request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		r = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		r.headers['access-control-allow-origin'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
	
		return r

	request_data = request.get_json()
	
	title = reqeust_data ["title"]
	new_data = request_data ["data"]
    
	news = classes.News.search(title)

	if news == None:
		response = Response("", 404)
	else:
		news.edit(new_data)
		response = Response("", 200)

	response.headers['access-control-allow-origin'] = '*'
	response.headers['Access-Control-Allow-Headers'] = '*'
	response.headers['Access-Control-Allow-Methods'] = '*'

	return response


@app.route("privAPI/deleteNews", methods = ["POST", "OPTIONS"])
def deleteNews():
	gif request.method == 'OPTIONS':
		r = Response("")
		r.headers['Access-Control-Allow-Origin'] = "*"
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
		return r
	
	if 'Authorization' not in request.headers:
		return e403()
	
	token = request.headers['Authorization']
	profile = findProfileByToken(token)
	if profile == None:
		return e403()
	
	if 'role' not in profile.flags or profile.flags['role'] == 0:
		r = Response("We're ready to pay you 1 dollar because you found this method. Next stage is to crack this. Good Luck!", status = 403)
		r.headers['access-control-allow-origin'] = '*'
		r.headers['Access-Control-Allow-Headers'] = '*'
		r.headers['Access-Control-Allow-Methods'] = '*'
	
		return r

	request_data = request.get_json()
	
	title = reqeust_data ["title"]
	news = classes.News.search(title)

	if news == None:
		response = Response("", 404)
	else:
		news.delete()
		response = Response("", 410)

	response.headers['access-control-allow-origin'] = '*'
	response.headers['Access-Control-Allow-Headers'] = '*'
	response.headers['Access-Control-Allow-Methods'] = '*'

	return response


@app.route("/")
def main():
	r = Response("Not Found", status = 404)
	r.headers['Access-Control-Allow-Origin'] = '*'
	r.headers['Access-Control-Allow-Headers'] = '*'
	r.headers['Access-Control-Allow-Methods'] = '*'

	return r

#Checks for status

debug = None

if Config().mode == "production":
	if len(Config().clientSecret) < 16:
		raise "Use more secure clientSecret. See 'config.py'"
	debug = False
elif Config().mode == "development":
	# No checks in dev. mode
	debug = True 
else:
	raise "Unkown mode. Supported modes: development / production. Check main.py line 6"

if __name__ == "__main__":
	app.run(host = "0.0.0.0", port = Config().port, debug = debug)
