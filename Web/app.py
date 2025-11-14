from flask import Flask
from storage import db, Monitor, User

app = Flask(__name__)
app.secret_key = "chave_super_secreta_123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

    # Criar monitor "Indefinido" apenas 1 vez
    if not Monitor.query.filter_by(nome="Indefinido").first():
        indef = Monitor(nome="Indefinido", telefone="-", disponibilidade=True)
        db.session.add(indef)
        db.session.commit()

    # Criar usuários padrão
    from werkzeug.security import generate_password_hash

    usuarios_padrao = [
        ("admin", "123", "admin"),
        ("empresa", "123", "empresa"),
        ("user", "123", "user"),
        ("monitor", "123", "monitor")
    ]

    for nome, senha, role in usuarios_padrao:
        if not User.query.filter_by(username=nome).first():
            novo = User(
                username=nome,
                senha=generate_password_hash(senha),
                role=role
            )
            db.session.add(novo)
    db.session.commit()

# IMPORT DEPOIS DE TUDO ACIMA
from routes import *

if __name__ == '__main__':
    app.run(debug=True)


#teste so para ver se ele atualiza o arquivo no git