import MySQLdb
from config import Config
from MySQLdb.cursors import DictCursor

def myConnect():
    return MySQLdb.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        passwd=Config.DB_PASSWORD,
        db=Config.DB_NAME, 
        cursorclass=DictCursor
    )
