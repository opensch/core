import os
import time
import json
import hashlib
import binascii

from flask import Response

import classes
from .helpers import *
from config import Config


def get_profile(school, request):
	if "Authorization" not in request.headers:
		return None

	token = request.headers["Authorization"]
	if (user_id := token_to_user_id(token)) is None:
		return None

	return classes.User.with_id(school, user_id)


def token_to_user_id(token):
	if os.path.exists(f"tokens/access/{token}"):
		with open(f"tokens/access/{token}") as file:
			contents = json.loads(file.read())
			if time.time() > contents["expires"]:
				return None
			else:
				return contents["uid"]
	else:
		return None


def whoami(request, school):
	if (profile := get_profile(school, request)) is None:
		return e403()

	profile.password = ""
	response = Response(json.dumps(profile.to_dict()), status = 200)
	response.headers['Content-Type'] = 'application/json'
	return response


def auth(request, school):
	args = request.form

	if 'login' in args and 'password' in args and 'clientID' in args:
		# Login and password in request, so we can try to auth user.

		if args['clientID'] != Config().clientID:
			return e403()

		if not (user := classes.User.with_login(school, args['login'])):
			return e400()

		if args['login'] == user.login:
			h = hashlib.sha512(args['password'].encode())
			if user.password == h.hexdigest():
				code = binascii.b2a_hex(os.urandom(15)).decode()
				with open('codes/' + code, 'w') as f:
					data = {}
					data['uid'] = user.uid
					data['time'] = time.time() + 300
					f.write(json.dumps(data))
				
				response = Response(code, status = 200)
				return response

		return e403()

	return e400()


def token_handler(request, school):
	args = request.form
	
	if "clientSecret" not in args:
		return e400()
	elif args["clientSecret"] != Config().clientSecret:
		return e403()

	access_hash = binascii.b2a_hex(os.urandom(32)).decode()	

	if "code" in args:
		token_data = read_code(args["code"])
		refresh_hash = binascii.b2a_hex(os.urandom(32)).decode()
	elif "refreshToken" in args:
		token_data = read_refresh_token(args["token"])
		refresh_hash = args["refreshToken"]
	else:
		return e400()

	if token_data == False:
		return e400()

	if Config().mode == "production":
		expiry_time = time.time() + 2592000
	else:
		expiry_time = time.time() + 1800
	
	access_data = {"uid": token_data["uid"], "expires": expiry_time}
	refresh_data = {"uid": token_data["uid"], "lastToken": access_hash}

	with open("tokens/access/" + access_hash, "w") as file:
		file.write(json.dumps(access_data))
	with open("tokens/refresh/" + refresh_hash, "w") as file:
		file.write(json.dumps(refresh_data))

	response = {
		"accessToken": access_hash,
		"refreshToken": refresh_hash,
		"expiresIn": expiry_time
	}

	response = Response(json.dumps(response), status = 200)
	response.headers["Content-Type"] = "application/json"
	return response


def read_code(code):
	code_file = "codes/" + code
	if os.path.exists(code_file) != True:
		return False
	
	with open(code_file) as file:
		token_data = json.loads(file.read())

	if token_data["time"] < time.time():
		os.remove(code_file)
		return False
	else:
		return token_data


def read_refresh_token(token):
	token_file = "tokens/refresh/" + token
	if os.path.exists(token_file) != True:
		return False
	
	with open(token_file) as file:
		token_data = json.loads(file.read())
	
	if os.path.exists("tokens/access/" + token_data["lastToken"]):
		os.remove("tokens/access/" + token_data["lastToken"])
	
	return token_data
