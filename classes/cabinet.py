class Cabinet(object):
	def __init__(self, school, dictionary_object = None):
		if dictionary_object is None:
			self.floor = -1
			self.nearby = []
			self.number = -1
			self.photo = ""
		else:
			if "_id" in dictionary_object.keys():
				del dictionary_object["_id"]
			self.__dict__ = dictionary_object

		self.school = school

	def to_dict(self):
		dictionary = self.__dict__.copy()
		del dictionary["school"]

		return dictionary

	def save_to_db(self):
		if self.school.database.cabinets.find_one(self.to_dict()):
			return None
		return self.school.database.cabinets.insert_one(self.to_dict())

	def delete(self):
		return self.school.database.cabinets.delete_one(self.to_dict())

	def search(school, query):
		objects = []
		results = list(school.database.cabinets.find(query))

		if len(results) == 0:
			return None

		for item in results:
			objects.append(Cabinet(school, item))

		return objects

	def with_floor(school, floor):
		return Cabinet.search(school, {"floor": floor})

	def with_number(school, number):
		if result := Cabinet.search(school, {"number": number}):
			return result[0]
		else:
			return None
