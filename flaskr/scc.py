from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('scc', __name__)

@bp.route('/')
def index():
    if g.user is None:
        return redirect(url_for('auth.login'))
    else:
        db = get_db()
        condition = db.execute(
        'SELECT condition'
        ' FROM scc where username = ?', (g.user['username'], )
        ).fetchone()
        return render_template('scc/index.html', condition=condition)
#def index():
#    db = get_db()
#    condition = db.execute(
#        'SELECT condition'
#        ' FROM scc where id = 1'
#    )
#    return render_template('scc/index.html', condition=condition)


@bp.route('/view/<string:username>')
def view(username):
    db = get_db()
    condition = db.execute(
        'SELECT condition'
        ' FROM scc WHERE username = ?', (username, )
    ).fetchone()
    print(condition[0])
    if condition[0] == "404":
        body = render_template('scc/' + condition[0] + '.html')
        return (body, 404)
    elif condition[0] == "500":
        body = render_template('scc/' + condition[0] + '.html')
        return (body, 500)
    else:
        return render_template('scc/' + condition[0] + '.html')
