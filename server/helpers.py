from flask import Response

def e400():
	return Response("Bad request", status = 400)


def e403():
	return Response("Not allowed", status = 403)


def e404():
	return Response("Not found", status = 404)


def e405():
	return Response("Method not allowed", status = 405)


def e500():
	return Response("Server Internal Error", status = 500)
