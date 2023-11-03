import logging
from flask import Flask, g, redirect, url_for, request, jsonify

import database
import settings

app = Flask('members api')
app.config['SECRET_KEY'] = settings.SECRET_KEY


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/members', methods=['GET'])
def get_members():
    db = database.get_db()
    cur = db.execute('select * from members')
    members = [dict(i) for i in cur.fetchall()]
    return jsonify(members)


@app.route('/members', methods=['POST'])
def add_member():
    new_member_data = request.get_json()
    db = database.get_db()
    try:
        cur = db.execute('insert into members (name, email, level) values (:name, :email, :level) returning *',
                         new_member_data)
        new_member_data = dict(next(cur))
        db.commit()
        print(cur)
        print(new_member_data)
        new_member_data['created'] = True
    except Exception as error:
        logging.exception(error)
        new_member_data['created'] = False

    return new_member_data


@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    db = database.get_db()
    cur = db.execute('select * from members where id = ?', [member_id])
    member = cur.fetchone()

    data = {'member': dict(member)}
    return data


@app.route('/members/<int:member_id>', methods=['PUT'])
def patch_member(member_id):
    member_data = request.get_json()
    parameters = [member_data.get('name'), member_data.get('email'), member_data.get('level'), member_id]
    print(parameters)

    db = database.get_db()
    cur = db.execute('update members set name = ?, email = ?, level = ? where id = ? returning *', parameters)
    data = next(cur)
    db.commit()

    return {'hello': 'world', 'member_id': member_id, 'parameters': parameters}


@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    return {'hello': 'world', 'member_id': member_id}


if __name__ == '__main__':
    with app.app_context():
        database.init()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
