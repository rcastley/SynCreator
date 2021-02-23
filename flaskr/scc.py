from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import time 

bp = Blueprint('scc', __name__)

@bp.route('/')
def index():
    if g.user is None:
        return redirect(url_for('auth.login'))
    else:
        db = get_db()
        condition = db.execute(
        'SELECT condition'
        ' FROM scc WHERE username = ?', (g.user['username'], )
        ).fetchone()
        return render_template('scc/index.html', condition=condition)


@bp.route('/set/<string:condition>')
def set(condition):
    if g.user is None:
        return redirect(url_for('auth.login'))
    else:
        db = get_db()
        db.execute(
            'UPDATE scc'
            ' SET condition = ? WHERE username = ?',
            (condition, g.user['username'])
        )
        db.commit()
        return redirect(url_for('index'))
    
    
@bp.route('/view/<string:username>')
def view(username):
    db = get_db()
    condition = db.execute(
        'SELECT condition'
        ' FROM scc WHERE username = ?', (username, )
    ).fetchone()
    if condition[0] == "404":
        resp = render_template('scc/' + condition[0] + '.html', condition=condition)
        return (resp, 404)
    elif condition[0] == "500":
        resp = render_template('scc/' + condition[0] + '.html', condition=condition)
        return (resp, 500)
    elif condition[0] == "timeout":
        time.sleep(60)
        return render_template('scc/' + condition[0] + '.html', condition=condition)
    elif condition[0] == "cookies":
        resp = make_response(render_template('scc/' + condition[0] + '.html', condition=condition))
        resp.set_cookie('SplunkSynthetic', 'abc123')
        return resp
    else:
        return render_template('scc/' + condition[0] + '.html', condition=condition)


@bp.route('/lorem')
def lorem():
    return render_template('scc/lorem.html')