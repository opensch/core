from .database import createMongo
import datetime
import json


class HomeworkObject(object):
	"""docstring for HomeworkObject"""
	def __init__(self):
		super(HomeworkObject, self).__init__()
		
		client = createMongo()
		self.db = client.usersHomework

		self.user_uid = None
		self.lessonDate = datetime.datetime(1900, 1, 1, 0, 0)
		self.lessonID = -1
		self.data = ""

	def toJSON(self):
		jsonTemp = {
			"user_uid": self.user_uid,
			"lessonDate": self.lessonDate.strftime('%d.%m.%Y'),
			"lessonID": self.lessonID,
			"data": self.data
		}
		return jsonTemp

	def fromJSON(json_data):
		temp_homework = HomeworkObject()
		
		temp_homework.user_uid   = json_data ["user_uid"]
		temp_homework.lessonDate = datetime.datetime.strptime(json_data ["lessonDate"], '%d.%m.%Y')
		temp_homework.lessonID   = json_data ["lessonID"]
		temp_homework.data       = json_data ["data"]
		   
		return temp_homework

	def createHomework (user, lessonDate, lessonID, data):
		new_homework = HomeworkObject()

		new_homework.user_uid = user.uid 
		new_homework.lessonDate = lessonDate
		new_homework.lessonID = lessonID
		new_homework.data = data

		new_homework.db.insert_one(new_homework.toJSON())

	def retrieveHomework (user, lessonDate, lessonID):
		homework_db = createMongo().usersHomework
		found_homework_objects = []

		lessonDate = lessonDate.strftime('%d.%m.%Y')
				
		search_query = {
				"user_uid": user.uid,
				"lessonDate": lessonDate,
				"lessonID": lessonID
			}
			
		found_homework = homework_db.find( search_query )

		for homework in found_homework:
			homework = HomeworkObject.fromJSON(homework)
			found_homework_objects.append(homework)

		return found_homework_objects

	def editHomework(self, new_homework):
		new_homework.user_uid = self.user_uid

		defHomework = HomeworkObject().toJSON()
		newHomework = new_homework.toJSON()

		for i in newHomework.keys():
			if newHomework [i] == defHomework [i]: newHomework [i] = self.toJSON() [i]

		new_homework = HomeworkObject.fromJSON(newHomework)

		db = createMongo().usersHomework

		query = {"$and": [
			{"user_uid": {"$eq": self.user_uid}},
			{"lessonDate": {"$eq": self.lessonDate.strftime('%d.%m.%Y')}},
			{"lessonID": {"$eq": self.lessonID}}
		]}

		c = db.update_one ( query, {"$set": new_homework.toJSON() } )

	def deleteHomework (self):
		self.db.delete_one(self.toJSON())

	def find (user_uid = None, lessonDate = None, lessonID = None):
		homework_db = createMongo().usersHomework
		query_dict = {"$and": []}

		if user_uid != None:
			query_dict['$and'].append({"user_uid": {"$eq": user_uid}})

		if lessonDate != None:
			query_dict['$and'].append({"lessonDate": {"$eq": lessonDate.strftime('%d.%m.%Y')}})

		if lessonID != None:
			query_dict['$and'].append({"lessonID": {"$eq": lessonID}})
		
		found_homework = homework_db.find( query_dict )
		temporary_array = []

		for homework in found_homework:
				homework = HomeworkObject.fromJSON(homework)
				temporary_array.append(homework)

		return temporary_array