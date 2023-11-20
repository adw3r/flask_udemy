from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import models
import settings

app = Flask('alchemy app')

app.config['SQLALCHEMY_DATABASE_URI'] = settings.DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['DEBUG'] = settings.APP_DEBUG

db = SQLAlchemy(model_class=models.Base)
db.init_app(app)


@app.route('/')
def get_members():
    members = db.session.query(models.Member).all()
    print(members)
    return [i.serialize for i in members]


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host=settings.APP_HOST, port=settings.APP_PORT)
