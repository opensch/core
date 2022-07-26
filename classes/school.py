from .database import createMongo
from .configReader import Config
import os
import json

class School():
    def __init__(self):
        self.name = ""
        self.database = None
        self.domain = ""
        self.email = ""

    def toJSON(self):
        dictionary = self.__dict__.copy()
        del dictionary["database"]
        return json.dumps(dictionary, sort_keys=True, indent=4)

    def fromJSON(json):
        school = School()
        school.name = json["name"]
        school.domain = json["domain"]
        school.database = createMongo(school.domain)
        school.email = json["email"]

        return school

    def createSchool(self):
        db = createMongo(Config().MONGO_DB_PREFIX, prefix = False)
        # check if school not in database
        if db.schools.find_one({"name": self.name}) is None:
            dictionary_object = self.__dict__.copy()
            del dictionary_object["database"]
            db.schools.insert_one(dictionary_object)
            return True

    def findSchool(name):
        db = createMongo(Config().MONGO_DB_PREFIX)
        # check if school not in database
        school = db.schools.find_one({"name": name})
        if school is None:
            return False
        else:
            return School.fromJSON(school)

    def findSchoolByDomain(domain):
        db = createMongo(Config().MONGO_DB_PREFIX, False)
        # check if school not in database
        school = db.schools.find_one({"domain": domain})
        if school is None:
            return False
        else:
            return School.fromJSON(school)
