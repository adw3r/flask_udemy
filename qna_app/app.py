from flask import Flask, render_template

import settings


app = Flask('qna application')


@app.route('/')
def index():
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
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
