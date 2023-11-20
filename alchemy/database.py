from flask_sqlalchemy import SQLAlchemy
import models

db = SQLAlchemy(model_class=models.Base)
