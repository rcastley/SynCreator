from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response, jsonify, abort, request
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import time
import requests

books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]

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


@bp.route('/controlgroups', methods=('GET', 'POST'))
def controlgroups():
    if g.user is None:
        return redirect(url_for('auth.login'))
    else:
        if request.method == 'POST':
            controlgroup = request.form['controlgroup']
            posttoken = request.form['posttoken']
        
        db = get_db()
        db.execute(
            'UPDATE scc'
            ' SET control_group = ?, post_token = ? WHERE username = ?',
            (controlgroup, posttoken, g.user['username'])
        )
        db.commit()
        return redirect(url_for('index'))


@bp.route('/set/<string:condition>', methods=('GET', 'POST'))
def set(condition):
    if g.user is None:
        return redirect(url_for('auth.login'))
    else:
        if g.user['control_group'] is not None:
            data = {
                'post_token' : g.user['post_token'],
                'command' : 'annotate',
                'title' : 'Condition changed',
                'message' : 'Using condition: ' + condition
            }
            requests.post('https://monitoring.rigor.com/control_groups/' + g.user['control_group'], data = data)
        db = get_db()
        db.execute(
            'UPDATE scc'
            ' SET condition = ? WHERE username = ?',
            (condition, g.user['username'])
        )
        db.commit()
        return redirect(url_for('index'))

@bp.route('/controlgroup/<string:condition>', methods=('GET', 'POST'))
def controlgroup(condition):
    print(condition)
    if g.user is None:
        return redirect(url_for('auth.login'))
    else:
        if g.user['control_group'] != 'None':
            if condition == 'depoy':
                data = {
                    'post_token' : g.user['post_token'],
                    'command' : 'annotate',
                    'title' : 'Deployment',
                    'message' : 'Front end deployed'
                }
            else:
                data = {
                    'post_token' : g.user['post_token'],
                    'command' : 'annotate',
                    'title' : 'Fix',
                    'message' : 'Fix for front end bug deployed'
                }
            requests.post('https://monitoring.rigor.com/control_groups/' + g.user['control_group'], data = data)
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
        time.sleep(62)
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


@bp.route('/api/v1/<string:username>/books/all', methods=['GET'])
def api_all(username):
    
    return jsonify(books)
    

@bp.route('/api/v1/<string:username>/books', methods=['GET'])
def api_id(username):
    # Check if an ID was provided as part of the URL.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."

    results = []

    for book in books:
        if book['id'] == id:
            results.append(book)

    if len(results) == 0:
        abort(404)

    return jsonify(results)


@bp.route('/api/v1/<string:username>/books', methods=['POST'])
def create_task(username):
    if not request.json or not 'title' in request.json:
        abort(400)
    book = {
        'id': books[-1]['id'] + 1,
        'title': request.json['title'],
        'author': request.json.get('author', "Not set"),
        'first_sentence': request.json.get('first_sentence', "Not set"),
        'year_published': request.json.get('year_published', "Not set")
    }
    return jsonify({'book': book}), 201


@bp.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)