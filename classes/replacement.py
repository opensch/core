class Replacement:
    def __init__(self, school, dictionary_object=None):
        if dictionary_object is None:
            self.lesson_id = None  # These two are required
            self.date = None
            self.subject = None  # These are optional
            self.position = None
            self.cabinet = None
            self.teacher = None
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
        lesson_db = self.school.database.lessons
        replacements_db = self.school.database.replacements

        # Before creating a replacement, let's check if the lesson with
        # the given identifier actually exists
        if not lesson_db.find_one({"id": self.lesson_id}):
            return None

        # Next, we check if there already is a replacement object
        # for the same lesson and date in the database
        query = {"lesson_id": self.lesson_id, "date": self.date}
        if replacements_db.find_one(query):
            return None

        replacement_query = {
            "lesson_id": self.lesson_id,
            "date": self.date,
            "subject": self.subject,
            "position": self.position,
            "cabinet": self.cabinet,
            "teacher": self.teacher,
        }
        return replacements_db.insert_one(replacement_query)

    def delete(self):
        query = {"lesson_id": self.lesson_id, "date": self.date}
        return self.school.database.replacements.delete_one(query)

    def search(school, query):
        found_objects = []
        results = school.database.replacements.find(query)

        for result in results:
            found_objects.append(Replacement(school, result))

        return found_objects

    def with_date(school, date):
        return Replacement.search(school, {"date": date})
