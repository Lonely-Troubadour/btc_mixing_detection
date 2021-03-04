from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import pymysql
import time
from datetime import datetime


def connect_prc():
    """
    This method connects to Bitcoin RPC.

    :returns: RPC connection. A connection to Bitcoin RPC.
    """
    RPC_USER = 'Alice'
    RPC_PASSWORD = '123456'
    RPC_PORT = 8332
    RPC_IP = '127.0.0.1'
    rpc_connection = AuthServiceProxy('http://%s:%s@%s:%d' % (RPC_USER, RPC_PASSWORD, RPC_IP, RPC_PORT), timeout=200000)
    return rpc_connection


def connect_mysql():
    """
    This method connects to MySql and return a connection.

    :returns: MySql connection. A connection to MySql database.
    """
    mysql_ip = "127.0.0.1"
    user = "admin"
    password = "admin123"
    db = "btc_transactions"
    mysql_connection = pymysql.connect(host=mysql_ip, user=user, password=password, db=db,
                                       cursorclass=pymysql.cursors.DictCursor)
    return mysql_connection

def get_time():
    return time.time()

def convert_time(ts):
    """This method converts timestamp to standard time format
    :param ts Timestamp
    :returns: Datetime. Standard time format.
    """
    int(ts)
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
