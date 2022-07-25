from .cabinet import Cabinet
from pymongo import ASCENDING
import json

class Lesson(object):
	"""docstring for Lesson"""
	def __init__(self, school, dataDict = None, rec = False):
		super(Lesson, self).__init__()
		self.rec = rec
		if dataDict == None:
			if rec == False:
				self.db = school.database.lessons
			self.replacement = False
			if rec == False:
				self.originalLesson = Lesson( school, rec = True ) # If replacement is true
			self.id = -1
			self.title = ""
			self.teacher = ""
			self.cabinet = None
			self.classNumber = -1
			self.classLetter = ""
		else:
			if "_id" in dataDict.keys():
				del dataDict["_id"]
			if "originalLesson" not in dataDict.keys():
				dataDict["originalLesson"] = Lesson(school)

			self.__dict__ = dataDict
			self.db = school.database.lessons

	def toJSON(self):
		dict =  self.__dict__.copy()
		
		if "originalLesson" in dict.keys():
			dict["originalLesson"] = dict["originalLesson"].toJSON()
		if "db" in dict.keys():
			del dict['db']

		return dict

	def createLesson(school, title, teacher, cabinet, classNumber, classLetter):
		tempLesson = {
			"title": title,
			"teacher": teacher,
			"cabinet": cabinet,
			"classNumber": classNumber,
			"classLetter": classLetter,
		}

		tempLesson = Lesson(school, tempLesson)

		c = tempLesson.db.find().sort( [ ("id", ASCENDING) ] )
		lID = 0
		for i in c:
			try:
				if i['id'] > lID:
					lID = i['id']
			except Exception:
				pass
		lID = lID + 1

		tempLesson.id = lID
		
		print(tempLesson.toJSON()) 
		tempLesson.db.insert_one(tempLesson.toJSON())

	def find(school, query, _filter="title"):
		db = school.database.lessons

		if _filter == "id":
			m = db.count_documents({"id": int(query)})
			c = db.find({"id": int(query)})

			if m != 1:
				return None

			return Lesson(school, c[0])

		if _filter == "title":
			c = db.find({"title": query})

			temp = []
			for i in c:
				temp.append(Lesson(school, i))

			return temp
		if _filter =="cabinet":
			c = db.find({"cabinet": query.toJSON()})

			temp = []
			for i in c:
				temp.append(Lesson(school, i))
			return temp
		if _filter == "teacher":
			c = db.find({"teacher": query})

			temp = []
			for i in c:
				temp.append(Lesson(school, i))

			return temp

	def findById(school, _id):
		return Lesson.find(school, _id, _filter="id")

	def findByTitle(school, title):
		return Lesson.find(school, title, _filter="title")

	def findByCabinet(school, cabinet):
		return Lesson.find(school, cabinet, _filter="cabinet")

	def findByCabinet(school, teacher):
		return Lesson.find(school, teacher, _filter="teacher")

	def removeLesson(self):
		self.db.delete_one({"id" : self.id})
