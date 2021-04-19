from flask import (
    Blueprint, g, redirect, render_template, request, url_for
)

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
