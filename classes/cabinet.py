from .database import createMongo
import json

class Cabinet(object):
	"""docstring for Cabinet"""
	def __init__(self):
		super(Cabinet, self).__init__()
		client = createMongo()
		self.db = client.cabinets
		self.floor = -1
		self.nearby = []
		self.number = -1
		self.photo = ""

	def fromJSON(data):
		tempCabinet = Cabinet()

		tempCabinet.floor = data['floor']
		tempCabinet.nearby = data['nearby']
		tempCabinet.number = data['number']
		tempCabinet.photo = data['photo']

		return tempCabinet

	def toJSON(self):
		jsonTemp = {
			"floor": self.floor,
			"nearby": self.nearby,
			"number": self.number,
			"photo": self.photo
		}
		return jsonTemp

	def createCabinet(floor, nearby, number, photo = ""):
		tempCabinet = Cabinet()
		tempCabinet.floor = floor
		tempCabinet.nearby = nearby
		tempCabinet.number = number

		if photo != "":
			tempCabinet.photo = photo

		client = createMongo()
		db = client.cabinets

		db.insert_one(tempCabinet.toJSON())

	def find(query, _filter='_id'):
			client = createMongo()
			db = client.cabinets

			if _filter == "floor":
				c = db.find({"floor": query})

				temp = []
				for i in c:
					temp.append(Cabinet.fromJSON(i))

				return temp

			if _filter == "number":
				m = db.count_documents({"number": int(query)})
				c = db.find({"number": int(query)})

				if m != 1:
					return None

				return Cabinet.fromJSON(c[0])

	def findByFloor(floor):
		return Cabinet.find(floor, _filter="floor")

	def findByNumber(number):
		return Cabinet.find(number, _filter="number")

	def removeCabinet(self):
		client = createMongo()
		db = client.cabinets

		number = self.number
		db.delete_one({"number" : number})
