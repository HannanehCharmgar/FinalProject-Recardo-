import sqlite3
from decouple import config
import time
from datetime import datetime

from logger import db_log

db_name = config("DATABASE_NAME")


class Account:
    table_name = "account"

    def __str__(self):
        return self.table_name

    def __init__(self):
        try:
            db_log.log("INFO", "create the account table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY,
                        telegramId INTEGER NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) 
                    )"""
            )
            connection.commit()
            connection.close()
        except Exception as err:
            db_log.log("ERROR", f"create the account table: {err}")

    def connect(self):
        connection = sqlite3.connect(f"{db_name}.db")
        cursor = connection.cursor()
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
					id INTEGER PRIMARY KEY,
					telegramId INTEGER NOT NULL,
					name VARCHAR(255) NOT NULL,
					email VARCHAR(255) 
				)"""
        )
        connection.commit()
        connection.close()

    def insert(self, telegramId: int, name: str, email: str = ""):
        try:
            db_log.log("INFO", "insert to account table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"INSERT INTO {self.table_name} VALUES (NULL, ?, ?, ?)",
                (telegramId, name, email),
            )
            connection.commit()
            connection.close()
        except Exception as err:
            db_log.log("ERROR", f"insert to account table: {err}")

    def all(self):
        try:
            db_log.log("INFO", "get all rows of account table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = cursor.fetchall()
            connection.close()
            result = []
            for item in rows:
                result.append(
                    {
                        "id": item[0],
                        "telegramId": item[1],
                        "name": item[2],
                        "email": item[3],
                    }
                )
            return result
        except Exception as err:
            db_log.log("ERROR", f"get all rows of account table: {err}")

    def find(self, telegramId: int):
        try:
            db_log.log("INFO", "find user of account table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE telegramId = ?", (telegramId,)
            )
            rows = cursor.fetchall()
            connection.close()

            result = []
            for item in rows:
                result.append(
                    {
                        "id": item[0],
                        "telegramId": item[1],
                        "name": item[2],
                        "email": item[3],
                    }
                )
            return result
        except Exception as err:
            db_log.log("ERROR", f"find user of account table: {err}")

    def findById(self, userId: int):
        try:
            db_log.log("INFO", "find user by id of account table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (userId,))
            rows = cursor.fetchall()
            connection.close()

            result = []
            for item in rows:
                result.append(
                    {
                        "id": item[0],
                        "telegramId": item[1],
                        "name": item[2],
                        "email": item[3],
                    }
                )
            return result
        except Exception as err:
            db_log.log("ERROR", f"find user by id of account table: {err}")

    def update(self, id: int, name: str, email: str):
        try:
            db_log.log("INFO", "update account table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"UPDATE {self.table_name} SET name=?, email=? WHERE id=?",
                (
                    name,
                    email,
                    id,
                ),
            )
            connection.commit()
            connection.close()
        except Exception as err:
            db_log.log("ERROR", "update account table: {err}")


class Reminder:
    table_name = "reminder"

    def __str__(self):
        return self.table_name

    def __init__(self):
        try:
            db_log.log("INFO", "create reminder table ")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        orginal_text VARCHAR(255) NOT NULL,
                        type VARCHAR(255),
                        remind_time VARCHAR(255),
                        request_time VARCHAR(255),
                        text VARCHAR(500),
                        status INTEGER
                    )"""
            )
            connection.commit()
            connection.close()
        except Exception as err:
            db_log.log("ERROR", f"create reminder table: {err}")

    def connect(self):
        connection = sqlite3.connect(f"{db_name}.db")
        cursor = connection.cursor()
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
					id INTEGER PRIMARY KEY,
					user_id INTEGER NOT NULL,
					orginal_text VARCHAR(255) NOT NULL,
					type VARCHAR(255),
					remind_time VARCHAR(255),
					request_time VARCHAR(255),
					text VARCHAR(500),
					status INTEGER
				)"""
        )
        connection.commit()
        connection.close()

    def insert(self, userId, orgText: str, data: dict):
        try:
            db_log.log("INFO", "insert to reminder table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"INSERT INTO {self.table_name} VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
                (
                    userId,
                    orgText,
                    data["type"],
                    data["time"],
                    data["timeRequest"],
                    data["text"],
                    0,
                ),
            )
            connection.commit()
            connection.close()
        except Exception as err:
            db_log.log("ERROR", f"insert to reminder table: {err}")

    def all(self):
        try:
            db_log.log("INFO", "get all rows of reminder table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = cursor.fetchall()
            connection.close()
            result = []
            for item in rows:
                result.append(
                    {
                        "id": item[0],
                        "user_id": item[1],
                        "orginal_text": item[2],
                        "type": item[3],
                        "time": item[4],
                        "timeRequest": item[5],
                        "text": item[6],
                        "status": item[7],
                    }
                )
            return result
        except Exception as err:
            db_log.log("ERROR", f"get all rows of reminder table: {err}")
            return []

    def find(self, id):
        try:
            db_log.log("INFO", "find in reminder table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = ?", (id,))
            rows = cursor.fetchall()
            connection.close()

            result = []
            for item in rows:
                result.append(
                    {
                        "id": item[0],
                        "user_id": item[1],
                        "orginal_text": item[2],
                        "type": item[3],
                        "time": item[4],
                        "timeRequest": item[5],
                        "text": item[6],
                        "status": item[7],
                    }
                )
            return result
        except Exception as err:
            db_log.log("ERROR", f"find in reminder table: {err}")
            return []

    def viewRemainder(self, userId, nowTime: str):
        try:
            db_log.log("INFO", f"view remainder of reminder table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE user_id = ? AND status = ?",
                (
                    userId,
                    0,
                ),
            )
            rows = cursor.fetchall()
            connection.close()

            format_datetime = "%H:%M:%S %Y/%m/%d"
            n_time_datetime = datetime.strptime(nowTime, format_datetime)

            result = []
            for item in rows:
                time_datetime = datetime.strptime(item[4], format_datetime)
                if time_datetime > n_time_datetime:
                    result.append(
                        {
                            "id": item[0],
                            "user_id": item[1],
                            "orginal_text": item[2],
                            "type": item[3],
                            "time": item[4],
                            "timeRequest": item[5],
                            "text": item[6],
                            "status": item[7],
                        }
                    )
            return result
        except Exception as err:
            db_log.log("ERROR", f"view remainder of reminder table: {err}")
            return []

    def update(self, id, field: str):
        try:
            db_log.log("INFO", "update in reminder table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            if field == "status":
                cursor.execute(
                    f"UPDATE {self.table_name} SET {field} = ? WHERE id = ?",
                    (
                        1,
                        id,
                    ),
                )
            connection.commit()
            connection.close()
        except Exception as err:
            db_log.log("ERROR", f"update in reminder table: {err}")

    def delete(self, id):
        try:
            db_log.log("INFO", "delete of reminder table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (id,))
            connection.commit()
            connection.close()
        except Exception as err:
            db_log.log("ERROR", "delete of reminder table: {err}")


class ToDoList:

    table_name = "todolist"

    def __str__(self):
        return self.table_name

    def __init__(self):
        try:
            db_log.log("INFO", "create todolist table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        orginal_text VARCHAR(255) NOT NULL,
                        text VARCHAR(500),
                        request_time VARCHAR(255),
                        status INTEGER,
                        today INTEGER
                    )"""
            )
            connection.commit()
            connection.close()
        except Exception as err:
            db_log.log("ERROR", f"create todolist table: {err}")

    def connect(self):
        connection = sqlite3.connect(f"{db_name}.db")
        cursor = connection.cursor()
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
					id INTEGER PRIMARY KEY,
					user_id INTEGER NOT NULL,
					orginal_text VARCHAR(255) NOT NULL,
					text VARCHAR(500),
					request_time VARCHAR(255),
					status INTEGER,
					today INTEGER
				)"""
        )
        connection.commit()
        connection.close()

    def insert(self, userId: int, orgText: str, text: str, timeReq: str):
        try:
            db_log.log("INFO", "insert to todolist table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"INSERT INTO {self.table_name} VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                (
                    userId,
                    orgText,
                    text,
                    timeReq,
                    0,
                    0,
                ),
            )
            connection.commit()
            connection.close()
        except Exception as err:
            db_log.log("ERROR", f"insert to todolist table: {err}")

    def all(self):
        try:
            db_log.log("INFO", "get all rows of todolist table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = cursor.fetchall()
            connection.close()
            result = []
            for item in rows:
                result.append(
                    {
                        "id": item[0],
                        "user_id": item[1],
                        "orginal_text": item[2],
                        "text": item[3],
                        "timeRequest": item[4],
                        "status": item[5],
                        "today": item[6],
                    }
                )
            return result
        except Exception as err:
            db_log.log("ERROR", f"get all rows of todolist table: {err}")
            return []

    def viewRemainder(self, userId: int):
        try:
            db_log.log("INFO", "view remainder of todolist table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE user_id = ? AND status = ?",
                (
                    userId,
                    0,
                ),
            )
            rows = cursor.fetchall()
            connection.close()

            result = []
            for item in rows:
                result.append(
                    {
                        "id": item[0],
                        "user_id": item[1],
                        "orginal_text": item[2],
                        "text": item[3],
                        "timeRequest": item[4],
                        "status": item[5],
                        "today": item[6],
                    }
                )
            return result
        except Exception as err:
            db_log.log("ERROR", f"view remainder of todolist table: {err}")
            return []

    def viewWorksToday(self, userId: int):
        try:
            db_log.log("INFO", "view works for today")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE user_id = ? AND status = ? AND today = ?",
                (
                    userId,
                    0,
                    1,
                ),
            )
            rows = cursor.fetchall()
            connection.close()

            result = []
            for item in rows:
                result.append(
                    {
                        "id": item[0],
                        "user_id": item[1],
                        "orginal_text": item[2],
                        "text": item[3],
                        "timeRequest": item[4],
                        "status": item[5],
                        "today": item[6],
                    }
                )
            return result
        except Exception as err:
            db_log.log("ERROR", f"view works for today: {err}")
            return []

    def update(self, id: int, field: str):
        try:
            db_log.log("INFO", "update the todolist table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            if field == "status" or field == "today":
                cursor.execute(
                    f"UPDATE {self.table_name} SET {field} = ? WHERE id = ?",
                    (
                        1,
                        id,
                    ),
                )
            connection.commit()
            connection.close()
        except Exception as err:
            db_log.log("ERROR", f"update the todolist table: {err}")

    def delete(self, id):
        try:
            db_log.log("INFO", "delete in todolist table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (id,))
            connection.commit()
            connection.close()
        except Exception as err:
            db_log.log("ERROR", f"delete in todolist table: {err}")


class History:

    table_name = "history_chat"

    def __init__(self):
        try:
            db_log.log("INFO", "create history table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        message_id INTEGER NOT NULL,
                        message_text VARCHAR(255) NOT NULL,
                        send_time VARCHAR(255),
                        who_sent INTEGER
                    )"""
            )
            connection.commit()
            connection.close()
        except Exception as err:
            db_log.log("ERROR", f"create history table:{err}")

    def connect(self):
        connection = sqlite3.connect(f"{db_name}.db")
        cursor = connection.cursor()
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
					id INTEGER PRIMARY KEY,
					user_id INTEGER NOT NULL,
					message_id INTEGER NOT NULL,
					message_text VARCHAR(255) NOT NULL,
					send_time VARCHAR(255),
                    who_sent INTEGER,
				)"""
        )
        connection.commit()
        connection.close()

    def insert(
        self, userId: int, messageId: int, messageText: str, timeReq: str, whoSent: int
    ):
        try:
            db_log.log("INFO", "insert to history table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"INSERT INTO {self.table_name} VALUES (NULL, ?, ?, ?, ?, ?)",
                (
                    userId,
                    messageId,
                    messageText,
                    timeReq,
                    whoSent,
                ),
            )
            connection.commit()
            connection.close()
        except Exception as err:
            db_log.log("ERROR", f"insert to history table: {err}")

    def viewByUserId(self, userId):
        try:
            db_log.log("INFO", "view by userId - history table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE user_id = ?", (userId,)
            )
            rows = cursor.fetchall()
            connection.close()

            result = []
            for item in rows:
                result.append(
                    {
                        "id": item[0],
                        "user_id": item[1],
                        "message_id": item[2],
                        "message_text": item[3],
                        "send_time": item[4],
                        "who_sent": item[5],
                    }
                )
            return result
        except Exception as err:
            db_log.log("ERROR", f"view by userId - history table: {err}")
            return []

    def viewByMessageId(self, messageId):
        try:
            db_log.log("INFO", "view by messageId - history table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE message_id = ?", (messageId,)
            )
            rows = cursor.fetchall()
            connection.close()

            result = []
            for item in rows:
                result.append(
                    {
                        "id": item[0],
                        "user_id": item[1],
                        "message_id": item[2],
                        "message_text": item[3],
                        "send_time": item[4],
                        "who_sent": item[5],
                    }
                )
            return result
        except Exception as err:
            db_log.log("ERROR", f"view by messageId - history table: {err}")
            return []

    def all(self):
        try:
            db_log.log("INFO", "get all - history table")
            connection = sqlite3.connect(f"{db_name}.db")
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = cursor.fetchall()
            connection.close()
            result = []
            for item in rows:
                result.append(
                    {
                        "id": item[0],
                        "user_id": item[1],
                        "message_id": item[2],
                        "message_text": item[3],
                        "send_time": item[4],
                        "who_sent": item[5],
                    }
                )
            return result
        except Exception as err:
            db_log.log("ERROR", f"get all - history table: {err}")
            return []
