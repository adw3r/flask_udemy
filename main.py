from flask import Flask, jsonify, request, url_for, redirect, session, render_template

PORT = 8000
HOST = '0.0.0.0'
DEBUG = True

app = Flask('flask_udemy')
app.config['SECRET_KEY'] = 'uniqueAndSecret'


@app.route('/', methods=['GET'])
def index():
    response = {'success': True}
    return jsonify(response)


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
    app.run(host=HOST, port=PORT, debug=DEBUG)
