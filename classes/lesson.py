class Lesson():
	def __init__(self, school, dictionary_object = None):
		if dictionary_object is None:
			self.id = None
			self.subject = None
			self.day = None
			self.position = None
			self.unique = False
			self.cabinet = None
			self.class_number = None
			self.class_letter = None
			self.teacher = None
		else:
			self.__dict__ = dictionary_object
			if "_id" in self.__dict__.keys():
				del self.__dict__["_id"]

		self.school = school

	def to_dict(self):
		dictionary = self.__dict__.copy()
		del dictionary["school"]
		return dictionary

	def to_old_dict(self):
		# This is used to provide backwards compatibility with the previous
		# versions still in use.
		return {
			"id": self.id,
			"title": self.subject,
			"teacher": self.teacher,
			"cabinet": self.cabinet,
			"classNumber": self.class_number,
			"classLetter": self.class_letter 
		}

	def save_to_db(self):
		database = self.school.database.lessons
		dictionary = self.to_dict()
		if database.count_documents(dictionary) > 0:
			return False

		# Getting an entry with the largest identifier
		dictionary["id"] = database.count_documents({})

		# Saving the new entry into the database
		return database.insert_one(dictionary)

	def save_changes(self):
		database = self.school.database.lessons
		return database.replace_one({"id": self.id}, self.to_dict())

	def delete(self):
		return self.school.database.lessons.delete_one({"id": self.id})

	def search(school, query):
		found_objects = []
		search_results = school.database.lessons.find(query)

		for result in search_results:
			found_objects.append(Lesson(school, result))

		return found_objects

	def with_id(school, id):
		if result := Lesson.search(school, {"id": id}):
			return result[0]
		else:
			return None

	def with_subject(school, subject_title):
		return Lesson.search(school, {"subject": subject_title})

	def with_day(school, day):
		return Lesson.search(school, {"day": day})

	def with_cabinet(school, cabinet_number):
		return Lesson.search(school, {"cabinet": cabinet_number})

	def with_class(school, number, letter):
		query = {"class_number": number, "class_letter": letter}
		return Lesson.search(school, query)

	def findByTeacher(school, teacher_id):
		return Lesson.search(school, {"teacher": teacher_id})