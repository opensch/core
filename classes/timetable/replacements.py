import json 
import datetime


class Replacement ():
	def __init__ (self, school, dataDict = None):
		if dataDict == None:
			self.date = ""
			self.classNumber = None
			self.classLetter = ""
			self.lessons = []
		else:
			if "_id" in dataDict.keys():
				del dataDict["_id"]
			self.__dict__ = dataDict

	def toJSON(self):
		dict =  self.__dict__
		del dict['db']

		return dict


	def create (school, date, position, classNumber, classLetter, oldLesson, newLesson):
		timetable_db = school.database.timetable
		replacements_db = school.database.replacements
		
		day = str(date.day)
		month = str(date.month)
		year = str(date.year)
		weekday = date.weekday()
	
		timetable_template = {
			"classNumber": int(classNumber),
			"classLetter": classLetter,
			"day": weekday
		}

		replacement_template = {
			"date": day + "." + month + "." + year,
			"classNumber": int(classNumber),
			"classLetter": classLetter,
		}
		
		timetable = timetable_db.find_one(timetable_template)
		replacement_entry = replacements_db.find_one(replacement_template)

		if timetable == None: 
			return None
		
		if replacement_entry == None:
			lenght = len(timetable["lessons"])

			replacement_entry = replacement_template
			replacement_entry["lessons"] = ['-' for i in range(lenght)]

			replacements_db.insert_one(replacement_entry)

		lessons = timetable["lessons"][position]
		oldID = str(oldLesson.id)
		newID = str(newLesson.id)

		if oldID in lessons:
			new_lessons = lessons.replace(oldID, newID)
			replacement_entry["lessons"][position] = new_lessons
		else:
			return None

		replacements_db.replace_one({"_id": replacement_entry["_id"]}, replacement_entry)
		return Replacement(school, replacement_entry)

	
	def edit (school, date, position, classNumber, classLetter, oldLesson, newLesson):
		replacements_db = school.database.replacements

		day = str(date.day)
		month = str(date.month)
		year = str(date.year)

		replacements_template = {
			"date": day + "." + month + "." + year,
			"classNumber": int(classNumber),
			"classLetter": classLetter
		}

		replacement_entry = replacements_db.find_one(replacements_template)
		print(replacement_entry)

		if replacement_entry == None:
			return None

		lessons = replacement_entry["lessons"][position]
		oldID = str(oldLesson.id)
		newID = str(newLesson.id)

		if oldID in lessons:
			new_lessons = lessons.replace(oldID, newID)
			replacement_entry["lessons"][position] = new_lessons
		else:
			return None

		replacements_db.replace_one(replacements_template, replacement_entry)

		del replacement_entry["_id"]
		return Replacement(school, replacement_entry)


	def delete (school, date, position, classNumber, classLetter):
		replacements_db = school.database.replacements

		day = str(date.day)
		month = str(date.month)
		year = str(date.year)

		replacements_template = {
			"date": day + "." + month + "." + year,
			"classNumber": int(classNumber),
			"classLetter": classLetter
		}

		replacement_entry = replacements_db.find_one(replacements_template)

		if replacement_entry == None:
			return None

		if position == "*":
			replacements_db.delete_one(replacement_entry)
		
		else:
			replacement_entry["lessons"][position] = '-'
			replacements_db.replace_one(replacements_template, replacement_entry)






