from flask_sqlalchemy import SQLAlchemy
from datetime import date


db = SQLAlchemy()

class Brinquedo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    tamanho = db.Column(db.String(50))
    preco = db.Column(db.Float, nullable=False)
    faixa_etaria = db.Column(db.String(50))
    caminho_imagem = db.Column(db.String(200))

class Monitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20))
    disponibilidade = db.Column(db.Boolean, default=True)  # True = disponível

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
    monitor_id = db.Column(db.Integer, db.ForeignKey('monitor.id'), nullable=True)
    monitor = db.relationship('Monitor', backref='orcamentos')
    status = db.Column(db.String(20), default='pendente')  # pendente | finalizado | cancelado


orcamento_brinquedo = db.Table('orcamento_brinquedo',
    db.Column('orcamento_id', db.Integer, db.ForeignKey('orcamento.id')),
    db.Column('brinquedo_id', db.Integer, db.ForeignKey('brinquedo.id'))
)

class Despesa(db.Model):
    __tablename__ = 'despesas'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, default=date.today)
