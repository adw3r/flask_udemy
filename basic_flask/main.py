from flask import Flask, jsonify, request, url_for, redirect, session, render_template, g
import sqlite3

import settings

app = Flask('flask_udemy')
app.config['SECRET_KEY'] = settings.SECRET_KEY


def connect_db():
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/viewresults', methods=['GET'])
def get_results_db():
    db = get_db()
    cur = db.execute('select * from test_table')
    results = cur.fetchall()
    values = [dict(i) for i in results]
    return jsonify(values)


@app.route('/results_form', methods=['GET', 'POST'])
def post_result():
    if request.method == 'GET':
        return '''
        <form method="POST" action="/results_form" enctype="application/json">
            <label>name</label>
            <input type="text" name="name">
            <label>username</label>
            <input type="text" name="username">
            <input type="submit" value="Submit">
        </form>
        '''
    else:
        values = request.form.to_dict()
        print(values)
        db = get_db()
        db.execute('insert into test_table (name, username) values (:name, :username)', values)
        db.commit()
        return redirect(url_for('get_results_db'))


@app.route('/favicon.ico')
def favicon():
    return ''


@app.route('/', methods=['GET'], defaults={'name': 'Stranger'})
@app.route('/<string:name>', methods=['GET'])
def index_parametr(name: str):
    display_param: bool = bool(int(request.values.get('display'))) if request.values.get('display') else False
    print(display_param)
    return render_template('index.html', user=name, display=display_param, mylist=[1, 2, 3, 4, 5, 6, 7, 8],
                           mydicts=[{'name': 'test', 'age': 1}, {'name': 'test2', 'age': 2},
                               {'name': 'test3', 'age': 3}, {'name': 'test4', 'age': 4}, ])


@app.route('/redir')
def redir():
    return redirect(url_for('index'))


@app.route('/parameter', methods=['GET', 'POST'], defaults={'name': 'empty'})
@app.route('/parameter/<string:name>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def index_name(name: str):
    session['name'] = name
    response = {'hello': name}
    return jsonify(response)


@app.route('/query')
def query_method():
    request_json = request.json()
    print(request_json)
    return jsonify({'query': request.args.to_dict()})


@app.route('/form', methods=['GET'])
def get_form():
    return render_template('form.html')


@app.route('/form', methods=['POST'])
def post_form():
    return f'<h1>Hello {request.form.to_dict()}</h1>'


if __name__ == '__main__':
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
