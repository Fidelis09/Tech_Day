from flask import Flask, render_template, request
from storage import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ADICIONE ESTA LINHA AQUI!
with app.app_context():
    db.create_all()

from routes import *

if __name__ == '__main__':
    app.run(debug=True)
