from flask import Flask, g, render_template, redirect, url_for, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import settings
import database

app = Flask('qna application')
app.config['SECRET_KEY'] = settings.SECRET_KEY


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_current_user():
    user_result = None
    if 'user' in session:
        user = session['user']
        db = database.get_db()
        user_cur = db.execute('select * from users where name = ?', [user])
        user_result = user_cur.fetchone()

    return user_result


@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/home')
def home():
    user = get_current_user()
    return render_template('pages/home.html', head_title=f'Questions & Answers', user=user)


@app.route('/logout')
def logout():
    del session['user']
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = database.get_db()
        form_to_dict = request.form.to_dict()
        cur = db.execute('select * from users where name = ?', [form_to_dict['name']])
        user_data = dict(cur.fetchone())
        if not user_data:
            error_message = 'User data is invalid!'
            return render_template('pages/login.html', head_title='Login', error_message=error_message)
        password_valid: bool = check_password_hash(user_data['password'], form_to_dict['password'])
        if password_valid:
            session['user'] = user_data['name']
            return redirect(url_for('home'))
        else:
            error_message = 'User data is invalid!'
            return render_template('pages/login.html', head_title='Login', error_message=error_message)
    return render_template('pages/login.html', head_title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        db = database.get_db()
        form_to_dict = request.form.to_dict()
        password_hash = generate_password_hash(form_to_dict['password'], method='pbkdf2:sha256:600000')
        user_name = form_to_dict['name']
        db.execute('insert into users (name, password, expert, admin) values (:name, :password, :expert, :admin)',
                   {'name': user_name, 'password': password_hash, 'expert': 0, 'admin': 0})
        db.commit()
        session['user'] = user_name
        return redirect(url_for('home'))
    return render_template('pages/register.html', head_title='Register')


@app.route('/question')
def question():
    user = get_current_user()
    return render_template('pages/question.html', head_title='Question', user=user)


@app.route('/ask')
def ask():
    user = get_current_user()
    return render_template('pages/ask.html', head_title='Ask a Question', user=user)


@app.route('/answer')
def answer():
    user = get_current_user()
    return render_template('pages/answer.html', head_title='Answer Question', user=user)


@app.route('/unanswered')
def unanswered():
    user = get_current_user()
    return render_template('pages/unanswered.html', head_title='Unanswered Questions', user=user)


@app.route('/promote/<user_id>')
def promote(user_id):
    db = database.get_db()
    db.execute('update users set expert = 1 where id = ?', [user_id])
    db.commit()
    return redirect(url_for('users'))


@app.route('/users')
def users():
    user = get_current_user()
    if user['admin']:
        db = database.get_db()
        users_cur = db.execute('select id, name, expert, admin from users')
        users_list = users_cur.fetchall()
        return render_template('pages/users.html', head_title='Users', user=user, users_list=users_list)


if __name__ == '__main__':
    with app.app_context():
        database.init()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
