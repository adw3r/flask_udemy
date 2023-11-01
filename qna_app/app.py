from flask import Flask, g, render_template, redirect, url_for, request

import settings
import database

app = Flask('qna application')
app.config['SECRET_KEY'] = settings.SECRET_KEY


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db = database.get_db()
    with open('schema.sql', encoding='utf-8') as file:
        sql_stmnt = file.read()
    db.executescript(sql_stmnt)
    db.commit()
    db.close()


@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/home')
def home():
    return render_template('pages/home.html', head_title='Questions & Answers')


@app.route('/login')
def login():
    return render_template('pages/login.html', head_title='Login')


@app.route('/register')
def register():
    return render_template('pages/register.html', head_title='Register')


@app.route('/question')
def question():
    return render_template('pages/question.html', head_title='Question')


@app.route('/ask')
def ask():
    return render_template('pages/ask.html', head_title='Ask a Question')


@app.route('/answer')
def answer():
    return render_template('pages/answer.html', head_title='Answer Question')


@app.route('/unanswered')
def unanswered():
    return render_template('pages/unanswered.html', head_title='Unaswered Questions')


@app.route('/users')
def users():
    return render_template('pages/users.html', head_title='Users')


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
