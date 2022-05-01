import sys
sys.path.append("..")

import classes

# DB FIXER 3000!

client = classes.createMongo()
db = client.users
n = db.find()

for i in n:
	profile = classes.User.fromJSON(i)

	print(profile.uid)
	profile.editUser(profile)