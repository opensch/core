from .database import createMongo
from .cabinet import Cabinet
import json

class Lesson(object):
	"""docstring for Lesson"""
	def __init__(self, rec = False):
		super(Lesson, self).__init__()
		self.rec = rec
		if rec == False:
			client = createMongo()
			self.db = client.lessons
		self.replacement = False
		if rec == False:
			self.originalLesson = Lesson( True ) # If replacement is true
		self.id = -1
		self.title = ""
		self.teacher = ""
		self.cabinet = Cabinet()
		self.classNumber = -1
		self.classLetter = ""

	def fromJSON(data):
		tempLesson = Lesson()

		tempLesson.id = data['id']
		tempLesson.title = data['title']
		tempLesson.teacher = data['teacher']
		tempLesson.cabinet = Cabinet.fromJSON(data['cabinet'])
		tempLesson.classNumber = data['classNumber']
		tempLesson.classLetter = data['classLetter']

		return tempLesson

	def toJSON(self):
		if self.rec == False:
			jsonTemp = {
				"replacement": self.replacement,
				"originalLesson": self.originalLesson.toJSON(),
				"id": self.id,
				"title": self.title,
				"teacher": self.teacher,
				"cabinet": self.cabinet.toJSON(),
				"classNumber": self.classNumber,
				"classLetter": self.classLetter
			}
		else:
			jsonTemp = {
				"replacement": self.replacement,
				"id": self.id,
				"title": self.title,
				"teacher": self.teacher,
				"cabinet": self.cabinet.toJSON(),
				"classNumber": self.classNumber,
				"classLetter": self.classLetter
			}	
		return jsonTemp

	def createLesson(title, teacher, cabinet, classNumber, classLetter):
		tempLesson = Lesson()
		tempLesson.title = title
		tempLesson.teacher = teacher
		tempLesson.cabinet = cabinet
		tempLesson.classNumber = classNumber
		tempLesson.classLetter = classLetter

		client = createMongo()
		db = client.lessons

		c = db.find().sort( [ ("id", ASCENDING) ] )
		lID = 0
		for i in c:
			try:
				if i['id'] > lID:
					lID = i['id']
			except Exception:
				pass
		lID = lID + 1

		tempLesson.id = lID

		db.insert_one(tempLesson.toJSON())

	def find(query, _filter="title"):
		client = createMongo()
		db = client.lessons

		if _filter == "id":
			m = db.count_documents({"id": int(query)})
			c = db.find({"id": int(query)})

			if m != 1:
				return None

			return Lesson.fromJSON(c[0])

		if _filter == "title":
			c = db.find({"title": query})

			temp = []
			for i in c:
				temp.append(Lesson.fromJSON(i))

			return temp
		if _filter =="cabinet":
			c = db.find({"cabinet": query.toJSON()})

			temp = []
			for i in c:
				temp.append(Lesson.fromJSON(i))
			return temp
		if _filter == "teacher":
			c = db.find({"teacher": query})

			temp = []
			for i in c:
				temp.append(Lesson.fromJSON(i))

			return temp

	def findById(_id):
		return Lesson.find(_id, _filter="id")

	def findByTitle(title):
		return Lesson.find(title, _filter="title")

	def findByCabinet(cabinet):
		return Lesson.find(cabinet, _filter="cabinet")

	def findByCabinet(teacher):
		return Lesson.find(teacher, _filter="teacher")

	def removeLesson(self):
		client = createMongo()
		db = client.lessons

		db.delete_one({"id" : self.id})