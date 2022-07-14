import tableM
import Camera

import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


class Db:
    """Класс создания подключения с использованием Singltone"""

    __instance__ = None
    instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = object.__new__(cls)
        return cls.instance

    @staticmethod
    def get_connect():
        return psycopg2.connect(database="Camera", user="", password="", host="localhost", port=5432)


# class Profile:
#     __slots__ = ["name", "lastname", "otch", "group", "login", "password", "age", "conn"]
#
#     def __init__(self):
#         self.conn = Db().get_connect()
#
#     def get_profile(self, login):
#         """Возвращает пароль из БД по введенному логину"""
#         password = TestSystem().get_list_like("password", "profile", "login", login)
#         return password
#
#     def set_profile(self, name, lastname, group, login, password, email):
#         """ полученные данные вносит в БД, проверяя существование группы"""
#         curs = self.conn.cursor()
#         password_hashed = bcrypt.hashpw(bytes(str(password), encoding="utf8"),
#                                         bcrypt.gensalt()).decode('utf-8')
#
#         id_group = TestSystem().get_list_like("id_group", "group", "name", group)
#
#         if len(id_group) == 0:
#             print("Такой группы нет! уточните номер группы и введите повторно данные")
#             Auth().registration()
#         else:
#             curs.execute(f"""INSERT INTO "profile" ("name", "lastname", "id_group", "login", "password", "email")
#             VALUES ('{name}', '{lastname}', '{id_group[0][0]}', '{login}', '{password_hashed}', '{email}')""")
#             self.conn.commit()

engine = create_engine("postgresql+psycopg2://postgres:@localhost/Camera")
Base = declarative_base()
Session = sessionmaker(bind=engine)
conn = engine.connect()
print(engine)

