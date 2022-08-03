from .database import database
from .configReader import Config
import os
import json

cached_schools = {}


class School:
    def __init__(self):
        self.name = ""
        self.database = None
        self.domain = ""
        self.email = ""

    def to_dict(self):
        dictionary = self.__dict__.copy()
        del dictionary["database"]
        return json.dumps(dictionary, sort_keys=True, indent=4)

    def from_dict(json):
        school = School()
        school.name = json["name"]
        school.domain = json["domain"]
        school.database = database(school.domain)
        school.email = json["email"]

        return school

    def createSchool(self):
        db = database(Config().MONGO_DB_PREFIX, prefix=False)
        # check if school not in database
        if db.schools.find_one({"name": self.name}) is None:
            dictionary_object = self.__dict__.copy()
            del dictionary_object["database"]
            db.schools.insert_one(dictionary_object)
            return True

    def with_name(name):
        db = database(Config().MONGO_DB_PREFIX, prefix=False)
        # check if school not in database
        school = db.schools.find_one({"domain": name})
        if school is None:
            return False
        else:
            return School.from_dict(school)

    def with_domain(domain):
        if domain in cached_schools.keys():
            return School.from_dict(cached_schools[domain])
        else:
            db = database(Config().MONGO_DB_PREFIX, prefix=False)

            school = db.schools.find_one({"domain": domain})
            if school is None:
                return False
            else:
                domain_name = school["domain"]
                cached_schools[domain_name] = school
                return School.from_dict(school)
