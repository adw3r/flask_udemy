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
    db = database.get_db()
    q_cur = db.execute('''
        select 
        questions.id as id, 
        questions.question as text, 
        users_experts.name as expert_name, 
        users_asked_by.name as asked_by_name 
        from questions 
        join users as users_asked_by on users_asked_by.id = questions.asked_by_id 
        join users as users_experts on users_experts.id = questions.expert_id
        where questions.answer_text is not Null
    ''')
    questions_data = q_cur.fetchall()
    print(questions_data)
    return render_template(
        'pages/home.html',
        head_title=f'Questions & Answers',
        user=user,
        questions_data=questions_data
    )


@app.route('/question/<int:question_id>')
def question(question_id):
    user = get_current_user()
    db = database.get_db()
    q_cur = db.execute('''
        select 
        questions.question as text, 
        questions.answer_text as answer, 
        users_experts.name as expert_name, 
        users_asked_by.name as asked_by_name 
        from questions 
        join users as users_asked_by on users_asked_by.id = questions.asked_by_id 
        join users as users_experts on users_experts.id = questions.expert_id
        where questions.id = ?
    ''', [question_id])
    question_data = q_cur.fetchone()
    print(question_data)
    return render_template('pages/question.html', head_title='Question', user=user, question=question_data)


@app.route('/logout')
def logout():
    if session.get('user'):
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


@app.route('/ask', methods=['GET', 'POST'])
def ask():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    db = database.get_db()
    experts_cur = db.execute('select id, name from users where expert = true')
    experts = experts_cur.fetchall()
    if request.method == 'POST':
        form_data = request.form.to_dict()
        insertion_data = form_data['question'], user['id'], form_data['expert_id']
        db.execute('insert into questions (question, asked_by_id, expert_id) values (?, ?, ?)', insertion_data)
        db.commit()

    return render_template('pages/ask.html', head_title='Ask a Question', user=user, experts=experts)


@app.route('/answer/<int:question_id>', methods=['GET', 'POST'])
def answer(question_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    db = database.get_db()
    if request.method == 'POST':
        db.execute('update questions set answer_text = ? where id = ?', [request.form['answer_text'], question_id])
        db.commit()
        return redirect(url_for('unanswered'))
    sql_stmt = '''
    select * from questions where questions.id = ?
    '''
    question_cur = db.execute(sql_stmt, [question_id])
    question_data = question_cur.fetchone()
    return render_template('pages/answer.html', head_title='Answer Question', user=user, question_data=question_data)


@app.route('/unanswered')
def unanswered():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    db = database.get_db()
    print(user)
    q_cur = db.execute(
        '''
        select questions.id, questions.question, users.name from questions 
        left join users on questions.asked_by_id = users.id 
        where questions.expert_id = ? and answer_text is Null
        ''',
        [user['id']]
    )
    questions = q_cur.fetchall()
    print(questions)
    return render_template('pages/unanswered.html', head_title='Unanswered Questions', user=user, questions=questions)


@app.route('/promote/<user_id>')
def promote(user_id):
    db = database.get_db()
    db.execute('update users set expert = 1 where id = ?', [user_id])
    db.commit()
    return redirect(url_for('users'))


@app.route('/users')
def users():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    if user['admin']:
        db = database.get_db()
        users_cur = db.execute('select id, name, expert, admin from users')
        users_list = users_cur.fetchall()
        return render_template('pages/users.html', head_title='Users', user=user, users_list=users_list)


if __name__ == '__main__':
    with app.app_context():
        database.init()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
