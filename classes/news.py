from .database import createMongo
import json

class News(object):
	"""docstring for News"""
	def __init__(self):
		super(News, self).__init__()
		client = createMongo()
		self.db = client.news
		self.id = -1
		self.title = ""
		self.isimportant = False
		self.newsText = ""

	def toJSON(self):
		jsonTemp = {
			"id": self.id,
			"title": self.title,
			"isimportant": self.isimportant,
			"newsText": self.newsText
		}
		return jsonTemp
		
	def fromJSON(data):
		tempNews = News()

		tempNews.id = data['id']
		tempNews.title = data['title']
		tempNews.isimportant = data['isimportant']
		tempNews.text = data['text']

		return tempNews

	def find(query, _filter='id'):
			client = createMongo()
			db = client.news

			if _filter == "id":
				c = db.find({"id": query})

				temp = []
				for i in c:
					temp.append(News.fromJSON(i))

				return temp

			
			if _filter == "title":
				c = db.find({"title": query})

				temp = []
				for i in c:
					temp.append(News.fromJSON(i))

				return temp

	def createNews(title, isimportant, text):
		tempNews = News()
		tempNews.title = title
		tempNews.isimportant = isimportant
		tempNews.text = text

		client = createMongo()
		db = client.news

		db.insert_one(tempNews.toJSON())

	def removeNews(self):
		client = createMongo()
		db = client.news

		db.delete_one({"id" : self.id})


	def findById(_id):
		return News.find(_id, _filter="id")

	def findByTitle(title):
		return News.find(title, _filter="title")