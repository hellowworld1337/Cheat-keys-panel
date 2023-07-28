from flask_login import UserMixin
from flask import url_for
from models import User
import sqlite3


def downloadkeys(count):
    sqlite_connection = sqlite3.connect('db.sqlite3')
    cursor = sqlite_connection.cursor()
    sql = f"SELECT * FROM key ORDER BY id DESC LIMIT {count}"
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    return data

def setkehwid(hwid, id):
    print(f"{hwid} | {id}")
    sqlite_connection = sqlite3.connect('db.sqlite3')
    cursor = sqlite_connection.cursor()
    sql = f"UPDATE key SET hwid='{hwid}' WHERE id={id}"
    cursor.execute(sql)
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()

def deletekey(id):
    sqlite_connection = sqlite3.connect('db.sqlite3')
    cursor = sqlite_connection.cursor()
    sql = f"DELETE FROM key WHERE id={id}"
    cursor.execute(sql)
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()

def startsub(time, id):
    print(f"{time} | {id}")
    sqlite_connection = sqlite3.connect('db.sqlite3')
    cursor = sqlite_connection.cursor()
    sql = f"UPDATE key SET end_work='{time}' WHERE id={id}"
    cursor.execute(sql)
    sqlite_connection.commit()
    sql = f"UPDATE key SET is_active=1 WHERE id={id}"
    cursor.execute(sql)
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()
    
def getallblacklist():
    sqlite_connection = sqlite3.connect('db.sqlite3')
    cursor = sqlite_connection.cursor()
    sql = "SELECT * FROM blacklist"
    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()
    sqlite_connection.close()
    meme = {}
    newmeme = []
    count = 0
    for i in data:
        meme[count] = i
        count += 1
    for k,v in meme.items():
        newmeme.append(v[1])
    return newmeme

def addbanhwid(hwid):
    sqlite_connection = sqlite3.connect('db.sqlite3')
    cursor = sqlite_connection.cursor()
    cursor.execute("INSERT INTO blacklist VALUES(NULL, ?)", (hwid,))
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()
    return True



def getallkeys():
    try:
        sqlite_connection = sqlite3.connect('db.sqlite3')
        cursor = sqlite_connection.cursor()
        print("База данных создана и успешно подключена к SQLite")
        sql = f"SELECT * FROM key"
        cursor.execute(sql)
        data = cursor.fetchall()
        fulldata = []
        for i in data:
            fulldata.append({'id':i[0], 'owner':i[1], 'game': i[2], 'key': i[3], 'hwid': i[4], 'can_reset': i[5],'is_active': i[6],'key_life': i[7],'end_work': i[8]})
        
        
        cursor.close()
        return fulldata

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")

def getUserr(user_id):
    try:
        sqlite_connection = sqlite3.connect('db.sqlite3')
        cursor = sqlite_connection.cursor()
        print("База данных создана и успешно подключена к SQLite")
        sql = f"SELECT * FROM user WHERE id = {user_id} LIMIT 1"
        cursor.execute(sql)
        data = cursor.fetchone()
        meme = {}
        newmeme = {}
        count = 0
        for i in data:
            meme[count] = i
            count += 1
        for k,v in meme.items():
            if k == 0:
                newmeme['id'] = str(v)
            elif k == 1:
                newmeme['username'] = str(v)
            elif k == 2:
                newmeme['password'] = str(v)
            elif k == 3:
                newmeme['invite_key'] = str(v)
            elif k == 4:
                newmeme['join_at'] = str(v)
        cursor.close()
        return newmeme

    except sqlite3.Error as error:
        print("Ошибка при подключении к sqlite", error)
    finally:
        if (sqlite_connection):
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


class UserLogin(UserMixin):
    def fromDB(self, user_id):
        self.__user = getUserr(user_id)
        print(self.__user)
        return self

    def is_autenticated(self):
        return True

    def create(self, user):
        self.__user = user
        return self
    
    def get_user(self):
        return self.__user

    def get_id(self):
        id = 0
        for i in self.__user:
            if i[0] == 'id':
                id = i[1]
        return str(id)