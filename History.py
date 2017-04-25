#!/usr/bin/env python
import sqlite3
from DataBase import path_to_db


class History:

    def __init__(self):
        self.db = sqlite3.connect(path_to_db)
        self.cursor = self.db.cursor()

    def insert_history(self, title, url, time, date):

        title = unicode(title)
        url = unicode(url)
        param = (title, url, time, date)
        self.cursor.execute(" INSERT INTO history(title, url, time, date) VALUES(?, ?, ?, ?) ", param)
        self.db.commit()
        self.db.close()

    def add_bookmark(self, title, url):
        title = unicode(title)
        url = unicode(url)
        param = (title, url)
        self.cursor.execute(" INSERT INTO bookmarks(title, url) VALUES(?, ?) ", param)
        self.db.commit()
        self.db.close()

    def remove_bookmark(self, title):
        title = unicode(title)
        self.cursor.execute("DELETE FROM bookmarks WHERE title = ?", (title,))
        self.db.commit()
        self.db.close()

    def get_bookmark_list(self):
        self.db = sqlite3.connect(path_to_db)
        self.db.text_factory = str
        self.cursor = self.db.cursor()
        self.cursor.execute("select title from bookmarks")
        row = self.cursor.fetchall()
        self.db.commit()
        self.db.close()
        return row
