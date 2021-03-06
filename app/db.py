import pymysql
from flask import g

def get_db():
    if 'db' not in g:
        g.db =  pymysql.connect(host='localhost', user="btc", password="btc", database="bitcoin")

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
