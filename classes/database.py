from pymongo import MongoClient, ASCENDING
from .configReader import Config

def createMongo():
	return MongoClient(Config().MONGO_HOST, Config().MONGO_PORT, username=Config().MONGO_USER, password=Config().MONGO_PASS)[Config().MONGO_DB]