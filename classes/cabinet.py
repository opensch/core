import json

class Cabinet(object):
	"""docstring for Cabinet"""
	def __init__(self, school, dataDict = None):
		super(Cabinet, self).__init__()
		if dataDict == None:
			self.floor = -1
			self.nearby = []
			self.number = -1
			self.photo = ""
		else:
			if "_id" in dataDict.keys():
				del dataDict["_id"]
			self.__dict__ = dataDict

		self.db = school.database.cabinets


	def toJSON(self):
		dict =  self.__dict__
		del dict['db']

		return dict

	def createCabinet(school, floor, nearby, number, photo = ""):
		tempCabinet = Cabinet(school)
		tempCabinet.floor = floor
		tempCabinet.nearby = nearby
		tempCabinet.number = number

		if photo != "":
			tempCabinet.photo = photo

		db = school.database.cabinets

		db.insert_one(tempCabinet.toJSON())

	def find(school, query, _filter='_id'):
			db = school.database.cabinets

			if _filter == "floor":
				c = db.find({"floor": query})

				temp = []
				for i in c:
					temp.append(Cabinet(school, i))

				return temp

			if _filter == "number":
				m = db.count_documents({"number": int(query)})
				c = db.find({"number": int(query)})

				if m != 1:
					return None

				return Cabinet(school, c[0])

	def findByFloor(school, floor):
		return Cabinet.find(school, floor, _filter="floor")

	def findByNumber(school, number):
		return Cabinet.find(school, number, _filter="number")

	def removeCabinet(self):
		number = self.number
		self.db.delete_one({"number" : number})
