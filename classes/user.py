import hashlib
import json

class User(object):
	"""docstring for User"""
	def __init__(self, school, dataDict = None):
		super(User, self).__init__()
		client = school.database

		if dataDict == None:
			self.db = client.users
			self.uid = -1
			self.surname = ""
			self.name = ""
			self.middleName = ""
			self.classNumber = -1
			self.classLetter = ""
			self.uniqLessons = []
			self.schoolName = school.name
			self.flags = { "role": 0 }
			#Role 0 is a regular user. Role 1 is an editor, who can create replacements.
			#In flags we can specify some properties for User, e.g. user need to change his password, user is Rodion, user was banned for something  
			
			self.tokens = []
			self.notifParams = {"10min": True, "homework": True, "homeworkTime": True, "replacements": True}

			self.login = ""
			self.password = "" # Use SHA-512 for it. Example: https://www.kite.com/python/examples/3144/hashlib-construct-a-sha512-hash-
		else:
			if "_id" in dataDict.keys():
				del dataDict["_id"]
			self.__dict__ = dataDict
			self.schoolName = school.name
			self.db = client.users

	def toJSON(self):
		dict =  self.__dict__
		del dict['db']
		del dict['schoolName']

		return dict

	def createUser(school, surname, name, middleName, classNumber, classLetter, login, password):
		tempUser = User(school)
		tempUser.surname = surname
		tempUser.name = name
		tempUser.middleName = middleName
		tempUser.classNumber = classNumber
		tempUser.classLetter = classLetter

		tempUser.login = login
		h = hashlib.sha512(password.encode())
		tempUser.password = h.hexdigest()

		c = tempUser.db.find().sort( [ ("id", ASCENDING) ] )
		lID = 0
		for i in c:
			try:
				if i['uid'] > lID:
					lID = i['uid']
			except Exception:
				pass
		lID = lID + 1

		tempUser.uid = lID

		tempUser.db.insert_one(tempUser.toJSON())

	def editUser(self, newUser):
		newUser.uid = self.uid

		defUser = User().toJSON()
		newUser = newUser.toJSON()
		for i in newUser:
			if newUser[i] == defUser[i]:
				newUser[i] = self.toJSON()[i]

		newUser = User.fromJSON(newUser)
		c = self.db.update_one( {"uid": self.uid}, {"$set": newUser.toJSON() })

	def find(school, query, _filter = 'login'):
		db = school.database.client.users

		if _filter == "all":
			c = db.find({})

			temp = []
			for i in c:
				temp.append( User(school, i) )
				
			return temp

		if _filter == "login":
			m = db.count_documents( {"login": query} )
			c = db.find( {"login": query} )

			if m != 1:
				return None

			return User(school, c[0])

		if _filter == "id":
			m = db.count_documents( {"uid": int(query)} )
			c = db.find( {"uid": int(query)} )

			if m != 1:
				return None

			return User(school, c[0])

		if _filter == "name":
			c = db.find( {"name": query} )

			temp = []
			for i in c:
				temp.append( User(school, i) )

			return temp

		if _filter == "surname":
			c = db.find( {"surname": query} )

			temp = []
			for i in c:
				temp.append( User(school, i) )

			return temp

		if _filter == "middleName":
			c = db.find( {"middleName": query} )

			temp = []
			for i in c:
				temp.append( User(school, i) )

			return temp

	def findById(school, _id):
		return User.find(school, _id, _filter = "id" )

	def findByLogin(school, login):
		return User.find(school, login, _filter = "login" )

	def findByName(school, name):
		return User.find(school, name, _filter = "name" )

	def findBySurname(school, surName):
		return User.find(school, surName, _filter = "surname" )

	def findByMiddlename(school, middleName):
		return User.find(school, middleName, _filter = "middlename" )

	def removeUser(self):
		self.db.delete_one({"uid" : self.uid})