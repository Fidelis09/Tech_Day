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
    
    novo_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return novo_id

def atualizar_brinquedo(brinquedo: Brinquedo):
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
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM brinquedos WHERE id = ?", (brinquedo_id,))
    conn.commit()
    conn.close()

# -------------------- AGENDAMENTOS --------------------
def carregar_agendamentos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, telefone, dia, mes, ano, inicio, fim, brinquedos, valor_total
        FROM agendamentos
    """) # <-- 1. SELECIONAR O ID
    linhas = cursor.fetchall()
    conn.close()

    agendamentos = []
    for linha in linhas:
        # 2. DESEMPACOTAR O ID
        id, nome, telefone, dia, mes, ano, inicio, fim, brinquedos, valor_total = linha
        brinquedos_lista = brinquedos.split(",") if brinquedos else []
        agendamentos.append(Agendamento(
            id=id, # <-- 3. PASSAR O ID PARA O MODELO
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
    
    novo_id = cursor.lastrowid # <-- 4. OBTER O ID DO NOVO AGENDAMENTO
    
    conn.commit()
    conn.close()
    return novo_id # <-- 5. RETORNAR O ID

# 6. NOVA FUNÇÃO PARA DELETAR AGENDAMENTO
def deletar_agendamento(agendamento_id: int):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agendamentos WHERE id = ?", (agendamento_id,))
    conn.commit()
    conn.close()