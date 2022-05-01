from ..database import createMongo

class Survey(object):
	"""docstring for """
	def __init__ (self):
		self.id=-1
		self.name=""
		self.description=""
		self.given_answers = [] 
		self.answer_variants = []
		self.state = True 


	def toJSON (self):
		jsonTemp = {
			"id": self.id,
			"name": self.name,
			"description":self.description,
			"given_answers": self.given_answers,
			"answer_variants": self.answer_variants,
			"state": self.state
		}
		return jsonTemp

	
	def fromJSON (data):
		converted_survey = Survey()

		converted_survey.id = data["id"]
		converted_survey.description = data["description"]
		converted_survey.name = data["name"]
		converted_survey.given_answers = data["given_answers"]
		converted_survey.answer_variants = data["answer_variants"]
		converted_survey.state = data["state"]

		return converted_survey

	
	def create (name, description, state, possible_answers):
		database = createMongo().surveys
		
		new_survey = Survey()
		
		new_survey.name = name
		new_survey.description = description
		new_survey.state = state
		new_survey.answer_variants = possible_answers
		
		used_ids = database.distinct("id")
		
		if used_ids:
			new_survey.id = used_ids[-1] + 1
		else:
			new_survey.id = 0
		
		database.insert_one(new_survey.toJSON())
		return new_survey

	
	def find (query, _filter="_id"):
		client = createMongo()
		db = client.surveys

		if _filter == "_id":
			count = db.count_documents({"id": int(query)})
			found_entry = db.find({"id": int(query)})

			if count != 1: return None

			return Survey.fromJSON(found_entry[0])

		if _filter == "name":
			count = db.count_documents({"name": int(query)})
			found_entry = db.find({"name": int(query)})

			if count != 1: return None

			return Survey.fromJSON(found_entry[0])

		if _filter == "description":
			count = db.count_documents({"description": int(query)})
			found_entry = db.find({"description": int(query)})

			if count != 1: return None

			return Survey.fromJSON(found_entry[0])


	def findById(_id):
		return Survey.find(_id, _filter="_id")


	def findByName(name):
		return Survey.find(name, _filter="name")


	def findByDescription(description):
		return Survey.find(description, _filter="description")


	def remove (self):
		survey_db = createMongo().surveys
		votes_db = createMongo().votes

		for response in self.given_answers:
			votes_db.delete_one({"id": response["id"]})

		survey_db.delete_one({"id": self.id})