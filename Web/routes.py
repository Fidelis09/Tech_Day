import os
import datetime
from app import app
from flask import render_template, request, redirect, url_for, current_app
from storage import Orcamento, db, Brinquedo
from werkzeug.utils import secure_filename

# Cadastro de Brinquedo (Admin)
@app.route('/admin', methods=['GET', 'POST'])
def pagina_admin():
    if request.method == 'POST':
        file = request.files['imagem']
        filename = secure_filename(file.filename)
        pasta_imagens = os.path.join(current_app.root_path, 'static', 'imagens')
        os.makedirs(pasta_imagens, exist_ok=True)
        file.save(os.path.join(pasta_imagens, filename))
        brinquedo = Brinquedo(
            nome=request.form['nome'],
            tamanho=request.form['tamanho'],
            preco=float(request.form['preco']),
            faixa_etaria=request.form['faixa_etaria'],
            caminho_imagem=filename
        )
        db.session.add(brinquedo)
        db.session.commit()
        return redirect('/admin')
    page_content = render_template('novo_brinquedo.html')
    return render_template(
        'home.html',
        active_page='admin',
        page_title='Painel do Administrador',
        page_content=page_content
    )

# Exclusão de Brinquedos Selecionados
@app.route('/excluir_selecionados', methods=['POST'])
def excluir_selecionados():
    ids = request.form.getlist('selecionados')
    for id in ids:
        brinquedo = Brinquedo.query.get(id)
        if brinquedo:
            caminho_arquivo = os.path.join(current_app.root_path, 'static', 'imagens', brinquedo.caminho_imagem)
            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)
            db.session.delete(brinquedo)
    db.session.commit()
    return redirect('/usuario')

# Página Inicial/Menu
@app.route('/')
def home():
    return render_template(
        'home.html',
        active_page='home',
        page_title='Bem-vindo!',
        page_content='<p>Escolha uma das opções no menu ao lado para começar.</p>'
    )

# Catálogo do Usuário
@app.route('/usuario')
def pagina_usuario():
    brinquedos = Brinquedo.query.all()
    page_content = render_template('catalogo.html', brinquedos=brinquedos)
    return render_template(
        'home.html',
        active_page='usuario',
        page_title='Catálogo de Brinquedos',
        page_content=page_content
    )

# Cadastro de Orçamento/Agendamento
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
        valor_total = sum(b.preco for b in selecionados)
        data_festa = datetime.datetime.strptime(data_festa_str, '%Y-%m-%d').date()
        hora_festa = datetime.datetime.strptime(hora_festa_str, '%H:%M').time()

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
        return redirect('/agendamentos')
    page_content = render_template('orcamentos.html', brinquedos=brinquedos)
    return render_template(
        'home.html',
        active_page='orcamentos',
        page_title='Realizar Orçamento',
        page_content=page_content
    )

# Listagem de Agendamentos
@app.route('/agendamentos')
def pagina_agendamentos():
    agendados = Orcamento.query.filter_by(agendado=True).all()
    page_content = render_template('agendamentos.html', agendados=agendados)
    return render_template(
        'home.html',
        active_page='agendamentos',
        page_title='Festas Agendadas',
        page_content=page_content
    )
