import json
from datetime import datetime

from flask import Response

import classes
from .helpers import *
from .authentication import get_profile


def timetable_today(request, school):
    return timetable(request, school, datetime.now())


def timetable_date(request, school, date):
    date = datetime.strptime(date, "%d.%m.%Y")
    return timetable(request, school, date)


def timetable(request, school, date):
    if (profile := get_profile(school, request)) is None:
        return e403()

    lessons_query = {
        "day": date.weekday(),
        "class_number": profile.classNumber,
        "class_letter": profile.classLetter,
    }
    replacements_query = {"date": date.strftime("%d.%m.%Y")}

    found_lessons = classes.Lesson.search(school, lessons_query)
    found_replacements = classes.Replacement.search(school, replacements_query)
    sorted_lessons = {}

    for lesson in found_lessons:
        if lesson.position not in sorted_lessons.keys():
            sorted_lessons[lesson.position] = classes.Lesson(school)

        if sorted_lessons[lesson.position].unique:
            pass
        elif lesson.unique and not sorted_lessons[lesson.position].unique:
            if lesson.id in profile.uniqLessons:
                sorted_lessons[lesson.position] = lesson
        else:
            sorted_lessons[lesson.position] = lesson

    timetable = []
    replacements = {item.lesson_id: item for item in found_replacements}

    for lesson in sorted_lessons.values():
        if lesson == classes.Lesson(school):
            pass

        if not replacements or lesson.id not in replacements.keys():
            is_replaced = False
            original_lesson = classes.Lesson(school)
        else:
            is_replaced = True
            original_lesson = lesson
            replacement = replacements[lesson.id]

            if replacement.subject:
                lesson.subject = replacement.subject
            if replacement.position:
                lesson.position = replacement.position
            if replacement.cabinet:
                lesson.cabinet = replacement.cabinet
            if replacement.teacher:
                lesson.teacher = replacement.teacher

        teacherUser = classes.User.with_id(school, int(lesson.teacher))
        if teacherUser != None:
            lesson.teacher = (
                teacherUser.surname
                + " "
                + teacherUser.name
                + " "
                + teacherUser.middleName
            )

        cabinet = classes.Cabinet.with_number(school, int(lesson.cabinet))
        if cabinet != None:
            lesson.cabinet = cabinet

        # This is a temporary measure to keep backwards compatibility
        # constructed_lesson = lesson.to_old_dict()
        # constructed_lesson["replacement"] = is_replaced
        # constructed_lesson["originalLesson"] = original_lesson.to_old_dict()
        # timetable.append(constructed_lesson)

    response = Response(json.dumps(timetable), status=200)
    response.headers["Content-Type"] = "application/json"
    return response


def get_classes(request, school):
    if (profile := get_profile(school, request)) is None:
        return e403()
    if "role" not in profile.flags or profile.flags["role"] == 0:
        return e403()

    timetable = school.database.timetable

    class_numbers = timetable.distinct("classNumber")
    class_letters = timetable.distinct("classLetter")

    all_classes = []

    for classNumber in class_numbers:
        for classLetter in class_letters:
            all_classes.append({"classNumber": classNumber, "classLetter": classLetter})

    response = Response(json.dumps(all_classes), status=200)
    response.headers["Content-Type"] = "application/json"
    return response


def get_class_timetable(request, school):
    if (profile := get_profile(school, request)) is None:
        return e403()
    if "role" not in profile.flags or profile.flags["role"] == 0:
        return e403()

    class_number = request.args.get("classNumber")
    class_letter = request.args.get("classLetter")

    if class_number is None or class_letter is None:
        return e400()

    query = {"class_number": int(class_number), "class_letter": class_letter}
    lessons = list(school.database.lessons.find(query))
    if len(lessons) == 0:
        return e404()

    final = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

    for lesson in lessons:
        del lesson["_id"]
        day = lesson["day"]
        final[day].append(lesson)

    response = Response(json.dumps(final), status=200)
    response.headers["Content-Type"] = "application/json"
    return response
