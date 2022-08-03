import os
import json

from flask import Response, make_response, send_file

import classes
from .helpers import *
from .authentication import get_profile


def handler(request, school, data):
    if (profile := get_profile(school, request)) is None:
        return e403()

    # If the user sends an encoded path, the built-in Flask
    # handlers don't follow the path. And so a user can access
    # any file on the server. So we clean up the path here.
    sanitized_path = ["cdn"]
    data = data.replace("%2F", "/")

    for directory in data.split("/"):
        if directory == ".." and len(sanitized_path) > 1:
            del sanitized_path[-1]
        elif directory == ".." and len(sanitized_path) == 1:
            return e404()
        elif directory == "." or directory == "":
            pass
        else:
            sanitized_path.append(directory)

    sanitized_path = "/".join(sanitized_path)

    if not os.path.exists(sanitized_path):
        return "Not Found", 404
    if os.path.isdir(sanitized_path):
        return "Not Found", 404

    fileExt = sanitized_path.split(".")[1]

    mime = "plain/text"

    if fileExt == "json":
        mime = "application/json"
    if fileExt == "pdf":
        mime = "application/pdf"
    if fileExt == "png":
        mime = "image/png"
    if fileExt == "gif":
        mime = "image/gif"
    if fileExt == ".html" or fileExt == ".htm":
        mime = "text/html"
    if fileExt == ".jpeg" or fileExt == ".jpg":
        mime = "image/jpeg"

    response = make_response(send_file(sanitized_path))
    response.headers["Content-Type"] = mime
    return response


def private_handler(request, school):
    if (profile := get_profile(school, request)) is None:
        return e403()
    if "role" not in profile.flags or profile.flags["role"] == 0:
        return e403()

    if request.method == "PUT":
        return create_news(request, school)
    if request.method == "POST":
        return edit_news(request, school)
    if request.method == "DELETE":
        return delete_news(request, school)


def create_news(request, school):
    request_data = request.get_json()

    title = request_data["title"]
    markdown_text = request_data["data"]
    is_important = request_data["important"]

    news = classes.News.create(title, markdown_text, is_important)

    if news != None:
        json_news = json.dumps(news.to_dict())
        response = Response(json_news, 200)
    else:
        response = Response("", 400)

    return response


def edit_news(request, school):
    request_data = request.get_json()

    title = request_data["title"]
    new_data = request_data["data"]

    news = classes.News.search(title)

    if news == None:
        response = Response("", 404)
    else:
        news.edit(new_data)
        response = Response("", 200)

    return response


def delete_news(request, school):
    request_data = request.get_json()

    title = request_data["title"]
    news = classes.News.search(title)

    if news == None:
        response = Response("", 404)
    else:
        news.delete()
        response = Response("", 410)

    return response
