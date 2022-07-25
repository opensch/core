import functions

routingMap = {
	#"": {"method": ["GET"], "function": functions.mainPage},
	"oauth/auth": {"method": ["POST"], "function": functions.auth},
    "oauth/token": {"method": ["POST"], "function": functions.token_handler},
    "oauth/whoami": {"method": ["GET"], "function": functions.whoami},
    "user/notifications": {"method": ["GET", "POST"], "function": functions.notifications_handler},
    "user/passwd": {"method": ["POST"], "function": functions.passwd},
    "homework/<date>/<lesson>": {"method": [ 'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS' ], "function": functions.homework_handler},
    "time": {"method": ["GET"], "function": functions.getTime},
    "times": {"method": ["GET"], "function": functions.getTimes},
    "timetable": {"method": ["GET"], "function": functions.timetableToday},
    "timetable/<date>": {"method": ["GET"], "function": functions.timetableDate},
    "lesson": {"method": ["GET"], "function": functions.lesson},
    "cabinet": {"method": ["GET"], "function": functions.cabinet},
    "cdn/<path:data>": {"method": ["GET"], "function": functions.cdn},
    "privAPI/getClasses": {"method": ["GET"], "function": functions.getClasses},
    "privAPI/getClassesTimetable": {"method": ["GET"], "function": functions.getClassTimetable},
    "privAPI/cabinet": {"method": ["GET", "POST", "DELETE"], "function": functions.priv_api_cabinet_handler},
    # TODO: create lesson
    # TODO: list lessons
    # TODO: remove lessons
    # TODO: create timetable for day
    # TODO: edit timetable for day
    # TODO: remove timetable for day
    "privAPI/createReplacement": {"method": ["POST"], "function": functions.createReplacement},
    "privAPI/editReplacement": {"method": ["POST"], "function": functions.editReplacement},
    "privAPI/deleteReplacement": {"method": ["GET"], "function": functions.deleteReplacement},
    "privAPI/getReplacements": {"method": ["GET"], "function": functions.getReplacements},
    "privAPI/createNews": {"method": ["POST"], "function": functions.createNews},
    "privAPI/editNews": {"method": ["POST"], "function": functions.editNews},
    "privAPI/deleteNews": {"method": ["POST"], "function": functions.deleteNews},
}
