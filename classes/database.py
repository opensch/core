from pymongo import MongoClient, ASCENDING
from .configReader import Config

_database_connection = MongoClient(
	Config().MONGO_HOST, 
	Config().MONGO_PORT, 
	username=Config().MONGO_USER, 
	password=Config().MONGO_PASS
)

def database(name, prefix = True):
	if prefix == False:
		return _database_connection[name]
	else:
		return _database_connection[Config().MONGO_DB_PREFIX + "-" + name]
