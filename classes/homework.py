import datetime
import json


class HomeworkObject(object):
	"""docstring for HomeworkObject"""
	def __init__(self, school, dataDict = None):
		super(HomeworkObject, self).__init__()

		if dataDict == None:
			self.user_uid = None
			self.lessonDate = datetime.datetime(1900, 1, 1, 0, 0)
			self.lessonID = -1
			self.data = ""
		else:
			if "_id" in dataDict.keys():
				del dataDict["_id"]
			self.__dict__ = dataDict
		self.school = school
		self.db = school.database.usersHomework


	def toJSON(self):
		dict =  self.__dict__
		del dict['db']

		return dict

	def createHomework (school, user, lessonDate, lessonID, data):
		new_homework = HomeworkObject(school)

		new_homework.user_uid = user.uid 
		new_homework.lessonDate = lessonDate
		new_homework.lessonID = lessonID
		new_homework.data = data

		new_homework.db.insert_one(new_homework.toJSON())

	def retrieveHomework (school, user, lessonDate, lessonID):
		homework_db = school.database.usersHomework
		found_homework_objects = []

		lessonDate = lessonDate.strftime('%d.%m.%Y')
				
		search_query = {
				"user_uid": user.uid,
				"lessonDate": lessonDate,
				"lessonID": lessonID
			}
			
		found_homework = homework_db.find( search_query )

		for homework in found_homework:
			homework = HomeworkObject(school, homework)
			found_homework_objects.append(homework)

		return found_homework_objects

	def editHomework(self, new_homework):
		new_homework.user_uid = self.user_uid

		defHomework = HomeworkObject(self.school).toJSON()
		newHomework = new_homework.toJSON()

		for i in newHomework.keys():
			if newHomework [i] == defHomework [i]: newHomework [i] = self.toJSON() [i]

		new_homework = HomeworkObject(self.school, newHomework)

		query = {"$and": [
			{"user_uid": {"$eq": self.user_uid}},
			{"lessonDate": {"$eq": self.lessonDate.strftime('%d.%m.%Y')}},
			{"lessonID": {"$eq": self.lessonID}}
		]}

		c = self.db.update_one ( query, {"$set": new_homework.toJSON() } )

	def deleteHomework(self):
		self.db.delete_one(self.toJSON())

	def find (school, user_uid = None, lessonDate = None, lessonID = None):
		homework_db = school.database.usersHomework
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
				homework = HomeworkObject(school, homework)
				temporary_array.append(homework)

		return temporary_array