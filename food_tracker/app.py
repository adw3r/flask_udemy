import datetime

from flask import Flask, g, render_template, redirect, url_for, request

import database
import settings

HTML_FROM_DATE_FORMAT = '%Y-%m-%d'
DB_DATE_FORMAT = '%Y%m%d'
PRETTY_DATE_FORMAT = '%B %d, %Y'

app = Flask('food_tracker')
app.config['SECRET_KEY'] = settings.SECRET_KEY


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db = database.get_db()
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
    db = database.get_db()
    if request.method == 'POST':
        entry_date = request.form.get('entry_date')  # YYYY-MM-DD
        print(entry_date)
        entry_date = datetime.datetime.strptime(entry_date, HTML_FROM_DATE_FORMAT).strftime(DB_DATE_FORMAT)
        db.execute('''insert into log_dates (entry_date) values (?)''', [entry_date])
        db.commit()
    sql_stmt = '''
        select entry_date, sum(proteins) as proteins, sum(carbs) as carbs, sum(fats) as fats, sum(calories) as calories from log_dates
            join food_date on food_date.log_dates_id = log_dates.id
            join foods on food_date.foods_id = foods.id
            group by log_dates.id
            order by entry_date asc
    '''
    cur = db.execute(sql_stmt)
    results = [
        {'pretty_date': datetime.datetime.strptime(str(row['entry_date']), DB_DATE_FORMAT).strftime(PRETTY_DATE_FORMAT),
         'backend_date': str(row['entry_date']), 'proteins': row['proteins'], 'carbs': row['carbs'],
         'fats': row['fats'], 'calories': row['calories'],

         } for row in cur.fetchall()]
    print(results)
    return render_template('pages/home.html', head_title='Home', results=results)


@app.route('/days', methods=['GET', 'POST'])
@app.route('/days/<date>', methods=['GET', 'POST'])
def day(date: str | None = None):
    if not date:
        return render_template('day.html', head_title='Day Details')

    db = database.get_db()
    date_cur = db.execute('select id, entry_date from log_dates where entry_date = ?', [date])
    food_cur = db.execute('select id, name from foods')
    log_cur = db.execute('''
    select name, proteins, carbs, fats, calories from log_dates 
    join 
    food_date on food_date.log_dates_id = log_dates.id 
    join foods on food_date.foods_id = foods.id 
    where log_dates.entry_date = ?''', [date])

    date_result = date_cur.fetchone()
    if request.method == 'POST':
        insertion_data = [request.form['food_selected'], date_result['id']]
        db.execute('insert into food_date (foods_id, log_dates_id) values (?, ?)', insertion_data)
        db.commit()
    log_results = log_cur.fetchall()

    totals = {'proteins': 0, 'carbs': 0, 'fats': 0, 'calories': 0, }

    for food in log_results:
        totals['proteins'] += food['proteins']
        totals['carbs'] += food['carbs']
        totals['fats'] += food['fats']
        totals['calories'] += food['calories']

    return render_template('pages/day.html', head_title='Day Details',
                           pretty_date=datetime.datetime.strptime(str(date_result['entry_date']),
                                                                  DB_DATE_FORMAT).strftime(PRETTY_DATE_FORMAT),
                           date=date, food_results=food_cur.fetchall(), log_results=log_results, totals=totals)


@app.route('/foods', methods=['POST', 'GET'])
def food():
    db = database.get_db()
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
    return render_template('pages/add_food.html', head_title='Add Food', foods_list=foods_list)


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
