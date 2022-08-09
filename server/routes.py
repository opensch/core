from . import authentication
from . import cabinet
from . import cdn
from . import homework
from . import lesson
from . import replacement
from . import times
from . import timetable
from . import user
from .setup import setupDummy


def mainPage(*args):
    return "Hello to openSchool!"

"""
    TODO:
        - Add a method to mark lesson as unique
        - Add a method to manage schools
        - Add a method to manage users
"""


routingMap = {
    "homePage": {"method": ["GET"], "function": mainPage},
    "oauth/auth": {"method": ["POST"], "function": authentication.auth},
    "oauth/token": {"method": ["POST"], "function": authentication.token_handler},
    "oauth/whoami": {"method": ["GET"], "function": authentication.whoami},
    "user/notifications": {
        "method": ["GET", "POST"],
        "function": user.notifications_handler,
    },
    "user/addToken": {"method": ["POST"], "function": user.addToken},
    "user/passwd": {"method": ["POST"], "function": user.passwd},
    "homework/<date>/<lesson>": {
        "method": ["GET", "POST", "PUT", "DELETE"],
        "function": homework.handler,
    },
    "time": {"method": ["GET"], "function": times.getTime},
    "times": {"method": ["GET"], "function": times.getTimes},
    "timetable": {"method": ["GET"], "function": timetable.timetable_today},
    "timetable/<date>": {"method": ["GET"], "function": timetable.timetable_date},
    "lesson": {"method": ["GET"], "function": lesson.handler},
    "replacement": {"method": ["GET"], "function": replacement.handler},
    "cabinet": {"method": ["GET"], "function": cabinet.handler},
    "cdn/<path:data>": {"method": ["GET"], "function": cdn.handler},
    "privAPI/getClasses": {"method": ["GET"], "function": timetable.get_classes},
    "privAPI/getClassesTimetable": {
        "method": ["GET"],
        "function": timetable.get_class_timetable,
    },
    "privAPI/cabinet": {
        "method": ["GET", "POST", "DELETE"],
        "function": cabinet.private_handler,
    },
    "privAPI/lesson": {
        "method": ["GET", "POST", "DELETE"],
        "function": lesson.private_handler,
    },
    "privAPI/replacement": {
        "method": ["GET", "POST", "DELETE"],
        "function": replacement.private_handler,
    },
    "privAPI/news": {
        "method": ["PUT", "POST", "DELETE"],
        "function": cdn.private_handler,
    },
    "setup": {"method": ["GET", "POST"], "function": setupDummy},
}
