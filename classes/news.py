import os
import json
import hashlib


class News:
    """
    This is a news object represented in a Python class.

            One of the features of openSchool is the ability to communicate with
    the users (mostly students and their parents) about the happenings in
    the organization. This is mostly done by newsletters. Howerver,
    openSchool supports viewing and sending news via the API. This object
    is used to represent a piece of news in a more comfortable way to view
            and interact with internally.

            Currently, news are NOT stored in a database, but in the 'cdn/'
            subfolder of the project. This is done because it's a bit hard
            to store markdown files in a database. Screw it, let's spit it
            out! WE. ARE. LAZY. ASSES!
    """

    def __init__(self):
        self.title = ""
        self.picture = None
        self.content = ""
        self.important = False

    def to_dict(self):
        jsonTemp = {
            "title": self.title,
            "picture": self.picture,
            "content": self.content,
            "important": self.important,
        }
        return jsonTemp

    def from_dict(data):
        tempNews = News()

        tempNews.title = data["title"]
        tempNews.important = data["important"]
        tempNews.content = data["content"]

        return tempNews

    def create(title, markdownFile, important=False):
        # Reading he news list file

        with open("cdn/news.json", "r") as news_file:
            news_list = json.loads(news_file.read())

        # Checking if the provided title is not already used in another news.

        for news_entry in news_list:
            if title == news_entry["title"]:
                return None

        # Then saving the markdown contents into a separate file on the drive

        news_dict = {"data": markdownFile}
        filename = str(hashlib.sha256(title.encode()).hexdigest()) + ".json"

        with open("cdn/newsContent/" + filename, "w") as file:
            contents = json.dumps(news_dict)
            file.write(contents)

        # Creating a new entry in the news list

        new_entry = {
            "title": title,
            "important": important,
            "content": "newsContent/" + filename,
            "picture": None,
        }

        news_list.append(new_entry)

        # Writing the new entry list back into 'news.json' file

        with open("cdn/news.json", "w") as news_file:
            contents = json.dumps(news_list)
            news_file.write(contents)

        return News.from_dict(new_entry)

    def edit(self, new_markdown):
        # Firstly, let's check if the news is still in place

        with open("cdn/news.json", "r") as news_file:
            news_entries = json.loads(news_file.read())

        if self.to_dict() not in news_entries:
            return None

        # If it's still available, modify the contents

        with open("cdn/" + self.content, "w") as file:
            file_structure = {"data": new_markdown}
            contents = json.dumps(file_structure)
            file.write(contents)

    def delete(self):
        # Deleting the file contating the content

        os.remove("cdn/" + self.content)

        # Opening up the news list file and deleting the entry

        with open("cdn/news.json", "r") as news_file:
            news_list = json.loads(news_file.read())

        news_list.remove(self.to_dict())

        with open("cdn/news.json", "w") as news_file:
            contents = json.dumps(news_list)
            news_file.write(contents)

    def search(title):
        with open("cdn/news.json", "r") as news_file:
            news_list = json.loads(news_file.read())

        for news_entry in news_list:
            if news_entry["title"] == title:
                return News.from_dict(news_entry)

        return None

    def get_content(self):
        with open("cdn/" + self.content) as file:
            contents = json.loads(file.read())

        return contents["data"]
