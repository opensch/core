import hashlib
import json


class User:
    def __init__(self, school, dictionary_object=None):
        if dictionary_object is None:
            self.uid = -1
            self.surname = ""
            self.name = ""
            self.middleName = ""
            self.classNumber = -1
            self.classLetter = ""
            self.uniqLessons = []
            self.flags = {"role": 0}
            # Role 0 is a regular user. Role 1 is an editor, who can create replacements.
            # In flags we can specify some properties for User,
            # e.g. user need to change his password, user was banned for something
            self.tokens = []
            self.notifParams = {
                "10min": True,
                "homework": True,
                "homeworkTime": True,
                "replacements": True,
            }
            self.login = ""
            self.password = ""  # Use SHA-512 for it
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
        self.password = hashlib.sha512(self.password.encode()).hexdigest()
        self.uid = self.school.databse.users.count_documents({})

        return self.school.database.users.insert_one(self.to_dict())

    def save_changes(self, separate_user=None):
        query = {"uid": self.uid}
        return self.school.database.users.replace_one(query, self.to_dict())

    def delete(self):
        return self.school.database.users.delete_one(self.to_dict())

    def search(school, query):
        found_objects = []
        results = list(school.database.users.find(query))

        for result in results:
            found_objects.append(User(school, result))

        return found_objects

    def with_id(school, id):
        if result := User.search(school, {"uid": id}):
            return result[0]
        else:
            return None

    def with_login(school, login):
        if result := User.search(school, {"login": login}):
            return result[0]
        else:
            return None

    def with_name(school, name):
        return User.search(school, {"name": name})

    def with_surname(school, surname):
        return User.search(school, {"surname": surname})

    def with_middlename(school, middle_name):
        return User.search(school, {"middleName": middle_name})
