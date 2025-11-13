from flask import Flask, render_template, request
from storage import db, Monitor  # ✅ adiciona Monitor aqui

app = Flask(__name__)
app.secret_key = "chave_super_secreta_123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Cria as tabelas
with app.app_context():
    db.create_all()

    # ✅ Garante que o monitor "Indefinido" exista
    if not db.session.query(Monitor).filter_by(nome="Indefinido").first():
        monitor_indefinido = Monitor(nome="Indefinido", telefone="-", disponibilidade=True)
        db.session.add(monitor_indefinido)
        db.session.commit()

from routes import *

if __name__ == '__main__':
    app.run(debug=True)