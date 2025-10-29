import os
import datetime
from app import app
from flask import render_template, request, redirect, url_for, current_app, flash
from storage import Orcamento, db, Brinquedo, Monitor
from werkzeug.utils import secure_filename

# Cadastro de Brinquedo (Admin)
@app.route('/admin', methods=['GET', 'POST'])
def pagina_admin():
    if request.method == 'POST':
        tipo = request.form.get('tipo')

        if tipo == 'brinquedo':
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

        elif tipo == 'monitor':
            monitor = Monitor(
                nome=request.form['nome'],
                telefone=request.form['telefone'],
                disponibilidade=bool(int(request.form['disponibilidade']))
            )
            db.session.add(monitor)

        db.session.commit()
        flash("Cadastro realizado com sucesso!", "success")
        return redirect('/admin')

    page_content = render_template('admin.html')
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
    flash("Brinquedos selecionados excluídos com sucesso.", "success")
    return redirect('/usuario')

# Página Inicial / Dashboard
@app.route('/')
def home():
    hoje = datetime.date.today()
    mes = request.args.get('mes', type=int, default=hoje.month)
    ano = request.args.get('ano', type=int, default=hoje.year)

    # Quantidade de festas (mês)
    festas_mes = (
        Orcamento.query
        .filter(
            db.extract('month', Orcamento.data_festa) == mes,
            db.extract('year', Orcamento.data_festa) == ano,
            Orcamento.agendado == True
        )
        .count()
    )

    # Monitores com mais trabalhos (mês)
    monitores_top = (
        db.session.query(
            Monitor.nome.label('nome'),
            db.func.count(Orcamento.id).label('qtd')
        )
        .join(Orcamento, Orcamento.monitor_id == Monitor.id)
        .filter(
            db.extract('month', Orcamento.data_festa) == mes,
            db.extract('year', Orcamento.data_festa) == ano,
            Orcamento.agendado == True
        )
        .group_by(Monitor.id)
        .order_by(db.desc('qtd'))
        .limit(5)
        .all()
    )

    # Clientes que mais locaram (mês)
    clientes_top = (
        db.session.query(
            Orcamento.nome_cliente.label('nome'),
            db.func.count(Orcamento.id).label('qtd')
        )
        .filter(
            db.extract('month', Orcamento.data_festa) == mes,
            db.extract('year', Orcamento.data_festa) == ano,
            Orcamento.agendado == True
        )
        .group_by(Orcamento.nome_cliente)
        .order_by(db.desc('qtd'))
        .limit(5)
        .all()
    )

    # Brinquedos mais locados (mês) + valor no mês
    # Observação: usa o relacionamento Orcamento.brinquedos (many-to-many)
    brinquedos_top = (
        db.session.query(
            Brinquedo.nome.label('nome'),
            db.func.count(Orcamento.id).label('qtd'),
            db.func.sum(Brinquedo.preco).label('valor_mes')
        )
        .select_from(Orcamento)
        .join(Orcamento.brinquedos)  # requer relacionamento definido no modelo
        .filter(
            db.extract('month', Orcamento.data_festa) == mes,
            db.extract('year', Orcamento.data_festa) == ano,
            Orcamento.agendado == True
        )
        .group_by(Brinquedo.id)
        .order_by(db.desc('qtd'))
        .limit(5)
        .all()
    )

    page_content = render_template(
        'dashboard.html',
        mes=mes,
        ano=ano,
        festas_mes=festas_mes,
        monitores_top=monitores_top,
        clientes_top=clientes_top,
        brinquedos_top=brinquedos_top
    )

    return render_template(
        'home.html',
        active_page='home',
        page_title='Dashboard',
        page_content=page_content
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
    monitores = Monitor.query.filter_by(disponibilidade=True).all()

    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        brinquedos_ids = request.form.getlist('brinquedos')
        monitor_id = request.form.get('monitor_id')

        data_festa = datetime.datetime.strptime(request.form['data_festa'], '%Y-%m-%d').date()
        hora_festa = datetime.datetime.strptime(request.form['hora_festa'], '%H:%M').time()

        selecionados = Brinquedo.query.filter(Brinquedo.id.in_(brinquedos_ids)).all()
        valor_total = sum(b.preco for b in selecionados)

        monitor = Monitor.query.get(monitor_id)

        # Verifica se o monitor já tem festa nesta data
        ja_agendado = any(o.data_festa == data_festa for o in monitor.orcamentos)

        if ja_agendado:
            flash(f"O monitor {monitor.nome} já está agendado para esta data.", "error")
            return redirect('/orcamentos')

        # Cria o novo orçamento
        orcamento = Orcamento(
            nome_cliente=nome_cliente,
            telefone=telefone,
            endereco=endereco,
            brinquedos=selecionados,
            valor_total=valor_total,
            agendado=True,
            data_festa=data_festa,
            hora_festa=hora_festa,
            monitor_id=monitor_id
        )

        db.session.add(orcamento)
        db.session.commit()

        flash(f"Festa agendada! Monitor {monitor.nome} reservado para {data_festa.strftime('%d/%m/%Y')}.", "success")
        return redirect('/agendamentos')

    page_content = render_template('orcamentos.html', brinquedos=brinquedos, monitores=monitores)
    return render_template(
        'home.html',
        active_page='orcamentos',
        page_title='Realizar Orçamento',
        page_content=page_content
    )

# 💰 ROTA: /financeiro — Painel financeiro simplificado
import datetime
from flask import render_template, request
from storage import Orcamento, db, Despesa

# 💰 ROTA: /financeiro — Painel financeiro completo
import datetime
from flask import render_template, request, redirect, flash
from storage import Orcamento, db, Despesa

@app.route('/financeiro')
def pagina_financeiro():
    hoje = datetime.date.today()
    mes = request.args.get('mes', type=int, default=hoje.month)
    ano = request.args.get('ano', type=int, default=hoje.year)

    # RECEITAS DO MÊS
    receitas_mes = db.session.query(
        db.func.sum(Orcamento.valor_total)
    ).filter(
        db.extract('month', Orcamento.data_festa) == mes,
        db.extract('year', Orcamento.data_festa) == ano
    ).scalar() or 0.0

    # GASTOS FIXOS COM MONITORES
    gasto_por_monitor = 150.0
    eventos_mes = Orcamento.query.filter(
        db.extract('month', Orcamento.data_festa) == mes,
        db.extract('year', Orcamento.data_festa) == ano
    ).count()
    gastos_monitores = eventos_mes * gasto_por_monitor

    # OUTRAS DESPESAS
    outras_despesas = db.session.query(
        db.func.sum(Despesa.valor)
    ).filter(
        db.extract('month', Despesa.data) == mes,
        db.extract('year', Despesa.data) == ano
    ).scalar() or 0.0

    # LUCROS
    lucro_bruto = receitas_mes
    lucro_liquido = receitas_mes - (gastos_monitores + outras_despesas)

    # ESTATÍSTICAS ANUAIS
    meses = []
    lucros_mensais = []
    for m in range(1, 13):
        total = db.session.query(db.func.sum(Orcamento.valor_total)).filter(
            db.extract('month', Orcamento.data_festa) == m,
            db.extract('year', Orcamento.data_festa) == ano
        ).scalar() or 0.0
        meses.append(datetime.date(ano, m, 1).strftime('%b'))
        lucros_mensais.append(float(total))

    # RECEITA FUTURA
    receitas_futuras = db.session.query(
        db.func.sum(Orcamento.valor_total)
    ).filter(Orcamento.data_festa > hoje).scalar() or 0.0

    # Lista de despesas manuais para exibir
    despesas_mes = Despesa.query.filter(
        db.extract('month', Despesa.data) == mes,
        db.extract('year', Despesa.data) == ano
    ).order_by(Despesa.data.desc()).all()

    page_content = render_template(
        'financeiro.html',
        lucro_bruto=lucro_bruto,
        lucro_liquido=lucro_liquido,
        gastos_monitores=gastos_monitores,
        outras_despesas=outras_despesas,
        receitas_futuras=receitas_futuras,
        meses=meses,
        lucros_mensais=lucros_mensais,
        despesas_mes=despesas_mes,
        mes=mes,
        ano=ano,
        datetime=datetime
    )

    return render_template(
        'home.html',
        active_page='financeiro',
        page_title='Financeiro',
        page_content=page_content
    )


# ➕ Adicionar despesa manual
@app.route('/adicionar_despesa', methods=['POST'])
def adicionar_despesa():
    descricao = request.form.get('descricao')
    valor = float(request.form.get('valor') or 0)
    data = datetime.datetime.strptime(request.form.get('data'), '%Y-%m-%d').date()

    nova = Despesa(descricao=descricao, valor=valor, data=data)
    db.session.add(nova)
    db.session.commit()
    flash(f"Despesa '{descricao}' adicionada com sucesso!", "success")
    return redirect('/financeiro')

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
