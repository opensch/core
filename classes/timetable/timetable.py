from ..configReader import Config

from ..lesson import Lesson
import json 
import datetime

class Timetable(object):
	# This is an important parameter. It controls the maximum lesson count
	# Change this parameter wisely as it can lead to crashes later.
	MAX_LESSON_COUNT = Config().MAX_LESSON_COUNT

	def __init__(self, school, dataDict = None):
		if dataDict == None:
			self.classNumber = -1
			self.classLetter = ""
			self.day = -1 # From 0 (Monday) to 6 (Sunday)
			self.lessons = []
		else:
			if "_id" in dataDict.keys():
				del dataDict["_id"]
			self.__dict__ = dataDict
		self.db = school.database.timetable

	def toJSON(self):
		dict =  self.__dict__
		del dict['db']

		return dict


	def init (school, class_number, class_letter, day, lesson_array):
		database = school.database.timetable

		database_request = {
			"classNumber": int(class_number),
			"classLetter": str(class_letter),
			"day": int(day)
		}

		# Checking if there is already a timetable
		matching_timetables = database.find(database_request)

		if matching_timetables.count() != 0:
			return None
		if len(lesson_array) > Timetable.MAX_LESSON_COUNT:
			return None

		formatted_array = ["-"] * Timetable.MAX_LESSON_COUNT
		
		for item in range(len(lesson_array)):
			formatted_array[item] = lesson_array[item]

		database_request["lessons"] = formatted_array
		response = database.insert_one(database_request)
	
		if response.acknowledged == True:
			return Timetable(school, database_request)
		else:
			return None


	def edit (self, new_lesson_array):
		database_request = {
			"classNumber": int(self.classNumber),
			"classLetter": str(self.classLetter),
			"day": int(self.day) 
		}

		# Just to check if the original timetable entry is untouched
		found_entry = self.db.find(database_request)

		if found_entry.count() != 1:
			return None
		if found_entry[0]["lessons"] != self.lessons:
			return None

		formatted_array = ["-"] * Timetable.MAX_LESSON_COUNT
		
		for item in range(len(new_lesson_array)):
			formatted_array[item] = new_lesson_array[item]

		query = {"_id": found_entry[0]["_id"]}
		replacement = database_request
		replacement["lessons"] = formatted_array 

		response = self.db.replace_one(query, replacement)

		if response.raw_result["ok"] == 1:
			self.lessons = formatted_array
			return True
		else:
			return None


	def delete (self):
		database_request = {
			"classNumber": int(self.classNumber),
			"classLetter": str(self.classLetter),
			"day": int(self.day) 
		}
		
		# Just to check if the original timetable entry is untouched
		found_entry = self.db.find(database_request)
		
		if found_entry.count() != 1:
			return None
		if found_entry[0]["lessons"] != self.lessons:
			return None

		query = {"_id", found_entry[0]["_id"]}
		response = self.db.delete_one(query)

		if response.raw_result["ok"] == 1:
			return True
		else:
			return None 


	def createTimetable(school, user, date):
		timetable_db = school.database.timetable
		replacements_db = school.database.replacements

		uL = user.uniqLessons
		cN = user.classNumber
		cL = user.classLetter

		day = date.weekday()

		if cL == "" and cN >= 10:
			cL = "A"

		timetable_request = {
			"classNumber": cN,
			"classLetter": cL,
			"day": day
		}

		replacement_request = {
			"date": str(date.day)+"."+str(date.month)+"."+str(date.year),
			"classNumber": cN,
			"classLetter": cL
		}

		timetable = timetable_db.find_one(timetable_request)
		replacements = replacements_db.find_one(replacement_request)

		if timetable: timetable = timetable ["lessons"]
		else: return None

		if replacements: replacements = replacements ["lessons"]
		else: replacements = None

		finalList = []

		# A for all class
		# I individual, use uniqLessons from user
		# , individual, use uniqLessons from user
		# Otherwise, all class

		for i in timetable:
			n = i
			
			if i == "-":
				finalList.append("-")
				continue
			if "A" not in n and "," not in n and "I" not in n:
				lesson = Lesson.findById(int(n))
				finalList.append(lesson) # Find lesson by ID
			if "A" in n:
				lesson = Lesson.findById(int(n.replace("A", "")))
				finalList.append(lesson)
			if "," in n or "I" in n:
				lessons = n.replace("I", "").split(",")
				a = 0
				for c in uL:
					if str(c) in lessons:
						finalList.append(Lesson.findById(int(c)))
						a = 1
				if a == 0:
					finalList.append("-")

		# REPLACEMENTS

		m = 0
		if replacements != None:
			for i in replacements:
				if i != "-":
					n = i
					if "A" not in n and "," not in n and "I" not in n:
						lesson = Lesson.findById(int(n))						
						lesson.replacement = True
						lesson.originalLesson = timetable[m]
						timetable[m] = lesson
					if "A" in n:
						lesson = Lesson.findById(int(n.replace("A", "")))
						lesson.replacement = True
						lesson.originalLesson = timetable[m]
						timetable[m] = lesson
					if "," in n or "I" in n:
						lessons = n.replace("I", "").split(",")
						a = 0
						for c in uL:
							if str(c) in lessons:
								lesson = Lesson.findById(int(c))
								lesson.replacement = True
								lesson.originalLesson = timetable[m]
								timetable[m] = lesson
								a = 1
						if a == 0:
							timetable[m] = "-"
				m += 1

		t = Timetable(school)
		t.classNumber = cN
		t.classLetter = cL
		t.day = day
		t.lessons = finalList

		return t
