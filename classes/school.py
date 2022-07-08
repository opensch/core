from .database import createMongo
from .configReader import Config
import os
import json

class School:
    def __init__(self):
        self.name = ""
        self.database = createMongo(self.name)
        self.domain = ""
        self.email = ""

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    def fromJSON(json):
        school = School()
        school.name = json["name"]
        school.domain = json["domain"]
        school.email = json["email"]

        return school

    def createSchool(self):
        db = createMongo(Config().MONGO_DB_PREFIX)
        # check if school not in database
        if db.schools.find_one({"name": self.name}) is None:
            db.schools.insert_one(self.toJSON())
            return True

    def findSchool():
        db = createMongo(Config().MONGO_DB_PREFIX)
        # check if school not in database
        school = db.schools.find_one({"name": self.name})
        if school is None:
            return False
        else:
            return School.fromJSON(school)
