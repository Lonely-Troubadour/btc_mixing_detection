from flask import (
    Blueprint, g, redirect, render_template, request, url_for, jsonify
)
import json
# from flaskext.mysql import MySQL
# import pymysql.cursors
from app.db import get_db

# mysql = MySQL(MYSQL_DATABASE_USER='btc', MYSQL_DATABASE_PASSWORD='BTC', MYSQL_DATABASE_DB='bitcoin')

bp = Blueprint('home', __name__)
@bp.route('/')
def index():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute('SELECT id FROM coinjoin ORDER BY id desc limit 1;')
        re = cursor.fetchone()
        coinjoin = re[0]+1

        cursor.execute('SELECT id FROM coinswap ORDER BY id desc limit 1;')
        re = cursor.fetchone()
        coinswap = re[0]+1

        cursor.execute('SELECT id FROM stealth_address ORDER BY id desc limit 1;')
        re = cursor.fetchone()
        stealth_address = re[0]+1
       
    all_info = {
        'all':100, 'fe':0, 'coinswap':coinswap, 'coinjoin':coinjoin, 'sa':stealth_address, 
        'block_count': 671795
    }
    return render_template('home/index.html', all_info=all_info)

@bp.route('/api/stats')
def get_stats():
    db = get_db()
    with db.cursor() as cursor:
        # sql = "SELECT * FROM (SELECT DATE_FORMAT(time, '%Y%m') days, count(id) count from coinjoin ORDER BY days DESC) AS tmp GROUP BY days;"
        sql = 'SELECT DATE_FORMAT(time, "%Y") ys, count(id) count FROM coinjoin GROUP BY ys;'
        cursor.execute(sql)
        re = cursor.fetchall()
        stat_coinjoin = dict(re)

        sql = 'SELECT DATE_FORMAT(time, "%Y") ys, count(id) count FROM coinswap GROUP BY ys;'
        cursor.execute(sql)
        re = cursor.fetchall()
        stat_coinswap = dict(re)

        sql = 'SELECT DATE_FORMAT(time, "%Y") ys, count(id) count FROM stealth_address GROUP BY ys;'
        cursor.execute(sql)
        re = cursor.fetchall()
        stat_sa = dict(re)

        stats = {
            'coinjoin': stat_coinjoin, 'coinswap': stat_coinswap, 'sa': stat_sa
        }

        print(stats)
        return jsonify(stats)


@bp.route('/api/overallStat')
def overallStat():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute('select date_format(time, "%Y%m%d") ys, count(id) count from coinswap group by ys;')
        res = cursor.fetchall();

    # print(res)
    return jsonify(res)

@bp.route('/api/statics')
def api_statics():
    tx_type = request.args.get('type')
    if tx_type == 'fe':
        return "0"
    elif tx_type == 'sa':
        table = 'stealth_address'
    else:
        table = tx_type

    print(table)
    
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute('select date_format(time, "%Y%m%d") ys, count(id) count from {} group by ys;'.format(table))
        res = cursor.fetchall();

    # print(res)
    return jsonify(res)

@bp.route('/statics')
def statics():
    tx_type = request.args.get('type')
    return render_template('statics.html', tx_type=tx_type)
