from ..database import createMongo
from .survey import Survey
import json


class Vote ():
	def __init__ (self):
		self.id = -1
		self.survey_id = -1
		self.user_id = -1
		self.answer = ""


	def toJSON(self, protected_mode = False):
		vote_json = {}

		vote_json["id"] = self.id
		vote_json["survey_id"] = self.survey_id
		vote_json["answer"] = self.answer

		if protected_mode == False:
			vote_json["user_id"] = self.user_id

		return vote_json


	def fromJSON(json_entry, protected_mode = False):
		converted_vote = Vote()
		
		converted_vote.id = json_entry["id"]
		converted_vote.survey_id = json_entry["survey_id"]
		converted_vote.answer = json_entry["answer"]

		if protected_mode == False:
			converted_vote.user_id = json_entry["user_id"]

		return converted_vote


	def cast (survey_id, user, answer):
		new_vote = {"user_id": user.uid, "survey_id": survey_id}
		survey = Survey.findById(survey_id)

		survey_db = createMongo().surveys
		votes_db = createMongo().votes

		if votes_db.find_one(new_vote):
			return None

		if survey == None:
			return None
		
		if answer not in survey.answer_variants:
			return None
		
		new_vote["answer"] = answer

		used_ids = votes_db.distinct("id")

		if used_ids: new_vote["id"] = used_ids[-1] + 1
		else:        new_vote["id"] = 0

		new_vote = Vote.fromJSON(new_vote)
		
		protected_vote = new_vote.toJSON(protected_mode = True)
		survey.given_answers.append(protected_vote)

		votes_db.insert_one(new_vote.toJSON())
		survey_db.replace_one({"id": survey.id}, survey.toJSON())
		
		return new_vote


	def remove (user, vote_id):
		survey_db = createMongo().surveys
		votes_db = createMongo().votes

		db_request = {"user_id": user.uid, "id": vote_id}
		found_entry = votes_db.find(db_request)

		if found_entry == None:
			return None

		vote = Vote.fromJSON(found_entry)
		survey = Survey.findById(vote.survey_id)
		survey.given_answers.remove(vote.toJSON(protected_mode = True))

		survey_db.replace_one({"id": survey.id}, survey.toJSON())
		vote_db.remove_one(vote.toJSON())


	def find (query, _filter = ("_id")):
		database = createMongo().votes

		if _filter == "_id":
			count = database.count_documents({"id": int(query)})
			found_entry = database.find({"id": int(query)})

			if count != 1: return None

			return Vote.fromJSON(found_entry[0])

		if _filter == "user_id":
			found_entries = database.find({"user_id": int(query)})
			
			entry_array = []

			for item in found_entries:
				item = Vote.fromJSON(item)
				entry_array.append(item)

			return entry_array 

		if __filter == "survey_id":
			count = database.count_documents({"survey_id": int(query)})
			found_entry = database.find({"survey_id": int(query)})

			if count != 1: return None

			return Vote.fromJSON(found_entry[0])

	
	def findById (identifier):
		return Vote.find(identifier, "_id")


	def findByUserId (user_id):
		return Vote.find(user_id, "user_id")


	def findBySurveyId (survey_id):
		return Vote.find(survey_id, "survey_id")