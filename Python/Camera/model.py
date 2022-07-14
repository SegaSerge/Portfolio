from flask import Flask
from flask_sqlalchemy import SQLAlchemy, SessionBase
from sqlalchemy import create_engine, select

engine = create_engine('postgresql+psycopg2://postgres:@localhost:5432/Camera', echo=True)
conn = engine.connect()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:@localhost:5432/Camera'
db = SQLAlchemy(app)
session = SessionBase


class Profile(db.Model):

    __tablename__ = 'Profile'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    surname = db.Column(db.String(120), unique=True, nullable=False)
    group = db.Column(db.String(20), unique=True, nullable=False)
    photo = db.Column(db.String(), unique=True, nullable=False)

    def __repr__(self):
        return f'<{id: } #{self.id}>'



