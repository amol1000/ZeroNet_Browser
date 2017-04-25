import sqlite3
import os


def find_path():
    path_to_db = "/home/"
    name = "Browser.py"

    for root, dirs, files in os.walk(path_to_db):
        if name in files:
            path_to_db = os.path.join(root,"Browser.db")
            break
    return path_to_db

path_to_db = find_path()
db = sqlite3.connect(path_to_db)
cursor = db.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS history'
               '(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,  url TEXT, time TEXT, date TEXT) ')

cursor.execute('''CREATE TABLE IF NOT EXISTS bookmarks(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT,  url TEXT) ''')


db.commit()
db.close()
