from flask import (
    Blueprint, g, redirect, render_template, request, url_for, jsonify
)
from app.db import get_db

bp = Blueprint('txs', __name__, url_prefix='/txs')

@bp.route('/fe', methods=('GET', 'POST'))
def fe():
    return render_template('transactions/list.html', tx_type='Fair Exchange')


@bp.route('/coinswap', methods=('GET', 'POST'))
def coinswap():
    return render_template('transactions/list.html', tx_type='CoinSwap')

@bp.route('/coinjoin', methods=('GET', 'POST'))
def coinjoin():
    return render_template('transactions/list.html', tx_type='CoinJoin')

@bp.route('/sa', methods=('GET', 'POST'))
def sa():
    return render_template('transactions/list.html', tx_type='Stealth Address')

@bp.route('/api/table/', methods=('GET', 'POST'))
def get_data():
    db = get_db()
    page = request.args.get('page')
    tx_type = request.args.get('type')

    pagination = 20
    current_page = pagination * (int(page) - 1)
    
    if tx_type == 'CoinSwap':
        table = 'coinswap'
        sql = "SELECT id, txid, next_txid, height, time FROM %s LIMIT %d, %d;" % (table, current_page, pagination)
    else:
        if tx_type == 'Fair Exchange':
            return "0"
        elif tx_type == 'CoinJoin':
            table = 'coinjoin'
        elif tx_type == 'Stealth Address':
            table = 'stealth_address'
            
        sql = "SELECT * FROM %s LIMIT %d, %d;" % (table, current_page, pagination)

    
    
    with db.cursor() as cursor:
        cursor.execute(sql)
        res = cursor.fetchall()
    # print(res)
    
    return jsonify(res)
