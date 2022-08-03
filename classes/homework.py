import datetime


class Homework:
    def __init__(self, school, dataDict=None):
        if dataDict is None:
            self.user_id = None
            self.lesson_id = None
            self.target_date = None
            self.data = ""
        else:
            if "_id" in dataDict.keys():
                del dataDict["_id"]
            self.__dict__ = dataDict

        self.school = school

    def to_dict(self):
        dict = self.__dict__.copy()
        del dict["school"]

        return dict

    def save_to_db(self):
        if self.school.database.homeworks.find_one(self.to_dict()):
            return None
        return self.school.database.homeworks.insert_one(self.to_dict())

    def save_changes(self):
        query = self.to_dict()
        del query["data"]

        if not self.school.database.homeworks.find_one(query):
            return None
        return self.school.database.homeworks.replace_one(query, self.to_dict())

    def delete(self):
        dictionary = self.to_dict()
        return self.school.database.homeworks.delete_one(dictionary)

    def search(school, query):
        results = list(school.database.homeworks.find(query))

        return [Homework(school, item) for item in results]

    def fetch(school, user_id, target_date, lesson_id):
        query = {"user_id": user_id, "target_date": target_date, "lesson_id": lesson_id}
        result = Homework.search(school, query)

        if len(result) > 1:
            return None

        return result

    def with_user_id(school, user_id):
        return Homework.search(school, {"user_id": user_id})
