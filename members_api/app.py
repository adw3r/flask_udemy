from flask import Flask, g, redirect, url_for

import database
import settings

app = Flask('members api')
app.config['SECRET_KEY'] = settings.SECRET_KEY


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/members', methods=['GET'])
def get_members():
    return {'hello': 'world'}


@app.route('/members', methods=['POST'])
def add_member():
    return {'hello': 'world'}


@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    return {'hello': 'world', 'member_id': member_id}


@app.route('/members/<int:member_id>', methods=['PUT', 'PATCH'])
def update_member(member_id):
    return {'hello': 'world', 'member_id': member_id}


@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    return {'hello': 'world', 'member_id': member_id}


if __name__ == '__main__':
    with app.app_context():
        database.init()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
