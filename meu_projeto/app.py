import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///brinquedos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# Modelos

class Brinquedo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    largura = db.Column(db.Float, nullable=False)
    altura = db.Column(db.Float, nullable=True)
    comprimento = db.Column(db.Float, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    imagem = db.Column(db.String(200))

class Orcamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    brinquedos = db.relationship('Brinquedo', secondary='orcamento_brinquedo')
    valor_total = db.Column(db.Float, nullable=False)
    agendado = db.Column(db.Boolean, default=False)
    data_festa = db.Column(db.Date, nullable=True)
    hora_festa = db.Column(db.Time, nullable=True)

orcamento_brinquedo = db.Table('orcamento_brinquedo',
    db.Column('orcamento_id', db.Integer, db.ForeignKey('orcamento.id')),
    db.Column('brinquedo_id', db.Integer, db.ForeignKey('brinquedo.id'))
)

with app.app_context():
    db.create_all()

# Rotas

@app.route('/')
def index():
    return redirect(url_for('cadastrar_brinquedo'))

# 1 Cadastro brinquedo
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_brinquedo():
    if request.method == 'POST':
        nome = request.form['nome']
        comprimento = float(request.form['comprimento'])
        largura = float(request.form['largura'])
        altura_str = request.form.get('altura')
        altura = float(altura_str) if altura_str else None
        valor = float(request.form['valor'])
        imagem_file = request.files['imagem']

        if imagem_file:
            filename = secure_filename(imagem_file.filename)
            imagem_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            caminho_imagem = filename  # só o nome do arquivo, sem o caminho
        else:
            caminho_imagem = ''

        brinquedo = Brinquedo(nome=nome, largura=largura, altura=altura,
                              comprimento=comprimento, valor=valor, imagem=caminho_imagem)
        db.session.add(brinquedo)
        db.session.commit()

        return redirect(url_for('catalogo'))

    return render_template('cadastrar.html')

# 2 Catálogo
@app.route('/catalogo')
def catalogo():
    brinquedos = Brinquedo.query.all()
    return render_template('catalogo.html', brinquedos=brinquedos)

# 3 Orçamentos
@app.route('/orcamentos', methods=['GET', 'POST'])
def orcamentos():
    brinquedos = Brinquedo.query.all()
    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        brinquedos_ids = request.form.getlist('brinquedos')
        data_festa_str = request.form['data_festa']
        hora_festa_str = request.form['hora_festa']

        selecionados = Brinquedo.query.filter(Brinquedo.id.in_(brinquedos_ids)).all()
        valor_total = sum(b.valor for b in selecionados)
    
        data_festa = datetime.strptime(data_festa_str, '%Y-%m-%d').date()
        hora_festa = datetime.strptime(hora_festa_str, '%H:%M').time()

        orcamento = Orcamento(
            nome_cliente=nome_cliente,
            telefone=telefone,
            endereco=endereco,
            brinquedos=selecionados,
            valor_total=valor_total,
            agendado=True,
            data_festa=data_festa,
            hora_festa=hora_festa
        )
        db.session.add(orcamento)
        db.session.commit()
        return redirect(url_for('agendamentos'))

    return render_template('orcamentos.html', brinquedos=brinquedos)

# 4 Agendamentos
@app.route('/agendamentos')
def agendamentos():
    agendados = Orcamento.query.filter_by(agendado=True).all()
    return render_template('agendamentos.html', agendados=agendados)

if __name__ == '__main__':
    app.run(debug=True)
