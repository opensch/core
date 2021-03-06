from ..database import createMongo
import json 
import datetime


class Replacement ():
	def __init__ (self):
		self.date = ""
		self.classNumber = None
		self.classLetter = ""
		self.lessons = []


	def toJSON (self):
		day = str(self.date.day)
		month = str(self.date.month)
		year = str(self.date.year)

		temp_json = {
			"date": day + "." + month + "." + year,
			"classNumber": self.classNumber,
			"classLetter": self.classLetter,
			"lessons": self.lessons
		}

		return json.dumps(temp_json)


	def fromJSON (json_entry):
		date = datetime.datetime.strptime(json_entry["date"], '%d.%m.%Y')

		replacement_object = Replacement()

		replacement_object.date = date
		replacement_object.classNumber = int(json_entry["classNumber"])
		replacement_object.classLetter = json_entry["classLetter"]
		replacement_object.lessons = json_entry["lessons"]

		return replacement_object


	def create (date, position, classNumber, classLetter, oldLesson, newLesson):
		timetable_db = createMongo().timetable
		replacements_db = createMongo().replacements
		
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
		return Replacement.fromJSON(replacement_entry)

	
	def edit (date, position, classNumber, classLetter, oldLesson, newLesson):
		replacements_db = createMongo().replacements

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
		return Replacement.fromJSON(replacement_entry)


	def delete (date, position, classNumber, classLetter):
		replacements_db = createMongo().replacements

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






