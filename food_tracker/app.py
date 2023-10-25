import datetime
import sqlite3

from flask import Flask, g, render_template, redirect, url_for, request

import settings

HTML_FROM_DATE_FORMAT = '%Y-%m-%d'
DB_DATE_FORMAT = '%Y%m%d'
PRETTY_DATE_FORMAT = '%B %d, %Y'

app = Flask('food_tracker')
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


def init_db():
    db = get_db()
    db.execute('''
    create table if not exists log_dates (
        id integer primary key autoincrement,
        entry_date date not null
    )
    ''')
    db.execute('''
    create table if not exists foods (
        id integer primary key autoincrement,
        name text not null,
        proteins integer not null,
        carbs integer not null,
        fats integer not null,
        calories integer not null
    )
    ''')
    db.execute('''
    create table if not exists food_date (
        foods_id     integer not null,
        log_dates_id integer not null,
        primary key (foods_id, log_dates_id)
    )
    ''')
    db.commit()
    db.close()


@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/home', methods=['POST', 'GET'])
def home():
    db = get_db()
    if request.method == 'POST':
        entry_date = request.form.get('entry_date')  # YYYY-MM-DD
        entry_date = datetime.datetime.strptime(entry_date, HTML_FROM_DATE_FORMAT).strftime(DB_DATE_FORMAT)
        db.execute('''insert into log_dates (entry_date) values (?)''', [entry_date])
        db.commit()
    cur = db.execute('select * from log_dates order by entry_date asc')
    results = [
        {'entry_date': datetime.datetime.strptime(str(i['entry_date']), DB_DATE_FORMAT).strftime(PRETTY_DATE_FORMAT)} for i in
        cur.fetchall()
    ]
    print(results)
    return render_template('home.html', head_title='Home', results=results)


@app.route('/days', methods=['POST', 'GET'])
@app.route('/days/<date>', methods=['GET'])
def day(date: str | None = None):
    if date:
        db = get_db()
        cur = db.execute('select entry_date from log_dates where entry_date = ?', [date])
        result = dict(cur.fetchone())
        date = datetime.datetime.strptime(str(result['entry_date']), DB_DATE_FORMAT).strftime(PRETTY_DATE_FORMAT)

        food_cur = db.execute('select id, name from foods')
        food_results = food_cur.fetchall()
        print(food_results)

        return render_template('day.html', head_title='Day Details', date=date, food_results=food_results)

    return render_template('day.html', head_title='Day Details')


@app.route('/foods', methods=['POST', 'GET'])
def food():
    db = get_db()
    if request.method == 'POST':
        values = request.form.to_dict()
        proteins = values.get('proteins')
        carbs = values.get('carbs')
        fats = values.get('fats')
        values['calories'] = int(proteins) * 4 + int(carbs) * 4 + int(fats) * 9
        db.execute('''
        insert into foods (name, proteins, carbs, fats, calories) values (:name, :proteins, :carbs, :fats, :calories)
        ''', values)
        db.commit()
    cur = db.execute('select * from foods')
    foods_list = cur.fetchall()
    return render_template('add_food.html', head_title='Add Food', foods_list=foods_list)


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
