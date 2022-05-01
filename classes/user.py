from .database import createMongo
import hashlib
import json

class User(object):
	"""docstring for User"""
	def __init__(self):
		super(User, self).__init__()
		client = createMongo()
		self.db = client.users
		self.uid = -1
		self.surname = ""
		self.name = ""
		self.middleName = ""
		self.classNumber = -1
		self.classLetter = ""
		self.uniqLessons = []
		self.flags = { "role": 0 }
		#Role 0 is a regular user. Role 1 is an editor, who can create replacements.
		#In flags we can specify some properties for User, e.g. user need to change his password, user is Rodion, user was banned for something  
		
		self.tokens = []
		self.notifParams = {"10min": True, "homework": True, "homeworkTime": True, "replacements": True}

		self.login = ""
		self.password = "" # Use SHA-512 for it. Example: https://www.kite.com/python/examples/3144/hashlib-construct-a-sha512-hash-

	def toJSON(self):
		jsonTemp = {
			"uid": self.uid,
			"surname": self.surname,
			"name": self.name,
			"middleName": self.middleName,
			"classNumber": self.classNumber,
			"classLetter": self.classLetter,
			"uniqLessons": self.uniqLessons,
			"login": self.login,
			"password": self.password,
			"tokens": self.tokens,
			"notifParams": self.notifParams,
			"flags": self.flags
		}
		return jsonTemp

	def fromJSON(data):
		tempUser = User()

		tempUser.uid = data['uid']
		tempUser.surname = data['surname']
		tempUser.name = data['name']
		tempUser.middleName = data['middleName']
		tempUser.classNumber = data['classNumber']
		tempUser.classLetter = data['classLetter']
		tempUser.uniqLessons = data['uniqLessons']
		tempUser.login = data['login']
		tempUser.password = data['password']
		tempUser.flags = data['flags']

		tempUser.tokens = data['tokens']
		tempUser.notifParams = data['notifParams']

		return tempUser

	def createUser(surname, name, middleName, classNumber, classLetter, login, password):
		tempUser = User()
		tempUser.surname = surname
		tempUser.name = name
		tempUser.middleName = middleName
		tempUser.classNumber = classNumber
		tempUser.classLetter = classLetter

		tempUser.login = login
		h = hashlib.sha512(password.encode())
		tempUser.password = h.hexdigest()

		client = createMongo()
		db = client.users

		c = db.find().sort( [ ("id", ASCENDING) ] )
		lID = 0
		for i in c:
			try:
				if i['uid'] > lID:
					lID = i['uid']
			except Exception:
				pass
		lID = lID + 1

		tempUser.uid = lID

		db.insert_one(tempUser.toJSON())

	def editUser(self, newUser):
		newUser.uid = self.uid

		defUser = User().toJSON()
		newUser = newUser.toJSON()
		for i in newUser:
			if newUser[i] == defUser[i]:
				newUser[i] = self.toJSON()[i]


		newUser = User.fromJSON(newUser)

		client = createMongo()
		db = client.users

		c = db.update_one( {"uid": self.uid}, {"$set": newUser.toJSON() })

	def find(query, _filter = 'login'):
		client = createMongo()
		db = client.users

		if _filter == "login":
			m = db.count_documents( {"login": query} )
			c = db.find( {"login": query} )

			if m != 1:
				return None

			return User.fromJSON(c[0])

		if _filter == "id":
			m = db.count_documents( {"uid": int(query)} )
			c = db.find( {"uid": int(query)} )

			if m != 1:
				return None

			return User.fromJSON(c[0])

		if _filter == "name":
			c = db.find( {"name": query} )

			temp = []
			for i in c:
				temp.append( User.fromJSON(i) )

			return temp

		if _filter == "surname":
			c = db.find( {"surname": query} )

			temp = []
			for i in c:
				temp.append( User.fromJSON(i) )

			return temp

		if _filter == "middleName":
			c = db.find( {"middleName": query} )

			temp = []
			for i in c:
				temp.append( User.fromJSON(i) )

			return temp

	def findById(_id):
		return User.find(_id, _filter = "id" )

	def findByLogin(login):
		return User.find(login, _filter = "login" )

	def findByName(name):
		return User.find(name, _filter = "name" )

	def findBySurname(surName):
		return User.find(surName, _filter = "surname" )

	def findByMiddlename(middleName):
		return User.find(middleName, _filter = "middlename" )

	def removeUser(self):
		client = createMongo()
		db = client.users

		db.delete_one({"uid" : self.uid})