from flask import Flask, render_template
from flask_table import Table, Col
from flask import jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app)
# mysql
mysql = MySQL(app)


# table
class ItemTable(Table):
    id = Col('id')
    txid = Col('txid')
    height = Col('height')
    time = Col('time')


class Item(object):
    def __init__(self, raw):
        self.id = raw[0]
        self.txid = raw[1]
        self.height = raw[2]
        self.time = raw[3]


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/multisig', methods=['GET'])
def data():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM multisig;''')
    result = cur.fetchall()
    # print(result)
    itemlist = [Item(row) for row in result]
    table = ItemTable(itemlist)
    # print(table)
    # print(table.__html__())
    return table.__html__()


@app.route('/fair_exchange', methods=['GET'])
def multisig():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM fair_exchange;''')
    result = cur.fetchall()
    # print(result)
    itemlist = [Item(row) for row in result]
    table = ItemTable(itemlist)
    print(table)
    return table.__html__()


@app.route('/analysis')
def analysis():
    cur = mysql.connection.cursor()
    # result = cur.execute('''SELECT COUNT(*) FROM transactions''')
    # tx_count = cur.fetchall()
    # print(tx_count)
    # result = cur.execute('''SELECT COUNT(*) FROM multisig''')
    # multisig_count = cur.fetchall()
    # print(multisig_count)
    # list = []
    # list.append({'value': tx_count[0][0], 'name': 'transactions'})
    # list.append({'value': multisig_count[0][0], 'name': 'multisig'})
    dict = {'transactions': 100000, 'multisig': 1000}

    return jsonify(dict)


@app.errorhandler(404)
def page_not_foud(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    app.run()
