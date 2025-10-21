# storage.py
import sqlite3
from models import Brinquedo, Agendamento

CAMINHO_DB = "brinquedos.db"

# -------------------- CONEXÃO --------------------
def conectar():
    conn = sqlite3.connect(CAMINHO_DB)
    return conn

# -------------------- CRIAR TABELAS --------------------
def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brinquedos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        tamanho TEXT,
        preco REAL,
        faixa_etaria TEXT,
        imagem TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        telefone TEXT,
        dia INTEGER,
        mes INTEGER,
        ano INTEGER,
        inicio INTEGER,
        fim INTEGER,
        brinquedos TEXT,
        valor_total REAL
    )
    """)

    conn.commit()
    conn.close()

# -------------------- BRINQUEDOS --------------------
def carregar_brinquedos():
    conn = conectar()
    cursor = conn.cursor()
    # 1. Carregar o ID
    cursor.execute("SELECT id, nome, tamanho, preco, faixa_etaria, imagem FROM brinquedos")
    linhas = cursor.fetchall()
    conn.close()
    return [Brinquedo(*linha) for linha in linhas]

def salvar_brinquedo(brinquedo: Brinquedo):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO brinquedos (nome, tamanho, preco, faixa_etaria, imagem)
        VALUES (?, ?, ?, ?, ?)
    """, (brinquedo.nome, brinquedo.tamanho, brinquedo.preco, brinquedo.faixa_etaria, brinquedo.imagem))
    
    # 2. Obter e retornar o ID do item recém-criado
    novo_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return novo_id # Retorna o ID

def atualizar_brinquedo(brinquedo: Brinquedo):
    # 3. Nova função de UPDATE
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE brinquedos 
        SET nome = ?, tamanho = ?, preco = ?, faixa_etaria = ?, imagem = ?
        WHERE id = ?
    """, (
        brinquedo.nome, 
        brinquedo.tamanho, 
        brinquedo.preco, 
        brinquedo.faixa_etaria, 
        brinquedo.imagem,
        brinquedo.id
    ))
    conn.commit()
    conn.close()

def deletar_brinquedo(brinquedo_id: int):
    # 4. Modificada para usar ID
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM brinquedos WHERE id = ?", (brinquedo_id,))
    conn.commit()
    conn.close()

# ... (Agendamentos permanecem iguais) ...

# -------------------- AGENDAMENTOS --------------------
def carregar_agendamentos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nome, telefone, dia, mes, ano, inicio, fim, brinquedos, valor_total
        FROM agendamentos
    """)
    linhas = cursor.fetchall()
    conn.close()

    agendamentos = []
    for linha in linhas:
        nome, telefone, dia, mes, ano, inicio, fim, brinquedos, valor_total = linha
        brinquedos_lista = brinquedos.split(",") if brinquedos else []
        agendamentos.append(Agendamento(
            nome=nome, telefone=telefone,
            dia=dia, mes=mes, ano=ano,
            inicio=inicio, fim=fim,
            brinquedos=brinquedos_lista,
            valor_total=valor_total
        ))
    return agendamentos

def salvar_agendamento(agendamento: Agendamento):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO agendamentos (nome, telefone, dia, mes, ano, inicio, fim, brinquedos, valor_total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        agendamento.nome,
        agendamento.telefone,
        agendamento.dia,
        agendamento.mes,
        agendamento.ano,
        agendamento.inicio,
        agendamento.fim,
        ",".join(agendamento.brinquedos),
        agendamento.valor_total
    ))
    conn.commit()
    conn.close()
