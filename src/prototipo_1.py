import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import json
import os
import shutil

# Caminhos
CAMINHO_BRINQUEDOS = 'brinquedos.json'
CAMINHO_AGENDAMENTOS = 'agendamentos.json'
PASTA_IMAGENS = 'imagens'

# Garante que a pasta de imagens exista
os.makedirs(PASTA_IMAGENS, exist_ok=True)

# Funções de leitura e escrita de JSON
def carregar_json(caminho):
    if os.path.exists(caminho):
        with open(caminho, 'r') as f:
            return json.load(f)
    return []

def salvar_json(caminho, dados):
    with open(caminho, 'w') as f:
        json.dump(dados, f, indent=4)

# Dados iniciais
brinquedos = carregar_json(CAMINHO_BRINQUEDOS)
agendamentos = carregar_json(CAMINHO_AGENDAMENTOS)

# Interface principal
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Brinquedos Infláveis")
        self.root.geometry("900x600")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        self.user_frame = ttk.Frame(self.notebook)
        self.admin_frame = ttk.Frame(self.notebook)
        self.agendamento_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.user_frame, text='Usuário')
        self.notebook.add(self.admin_frame, text='Admin')
        self.notebook.add(self.agendamento_frame, text='Agendamentos')

        self.setup_user_tab()
        self.setup_admin_tab()
        self.setup_agendamento_tab()

    # =================== ADMIN ===================
    def setup_admin_tab(self):
        frame = self.admin_frame

        tk.Label(frame, text="Nome do Brinquedo:").pack()
        self.nome_entry = tk.Entry(frame)
        self.nome_entry.pack()

        tk.Label(frame, text="Tamanho (Ex: 5x5m):").pack()
        self.tamanho_entry = tk.Entry(frame)
        self.tamanho_entry.pack()

        tk.Label(frame, text="Preço (R$):").pack()
        self.preco_entry = tk.Entry(frame)
        self.preco_entry.pack()

        tk.Label(frame, text="Faixa etária ideal (Ex: 3-10 anos):").pack()
        self.faixa_entry = tk.Entry(frame)
        self.faixa_entry.pack()

        self.caminho_imagem = None

        tk.Button(frame, text="Selecionar Imagem", command=self.selecionar_imagem).pack(pady=5)
        tk.Button(frame, text="Cadastrar Brinquedo", command=self.cadastrar_brinquedo).pack(pady=10)

    def selecionar_imagem(self):
        caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png *.jpeg")])
        if caminho:
            self.caminho_imagem = caminho
            messagebox.showinfo("Imagem selecionada", f"Imagem: {caminho}")

    def cadastrar_brinquedo(self):
        nome = self.nome_entry.get()
        tamanho = self.tamanho_entry.get()
        preco = self.preco_entry.get()
        faixa = self.faixa_entry.get()

        if not all([nome, tamanho, preco, faixa, self.caminho_imagem]):
            messagebox.showerror("Erro", "Preencha todos os campos e selecione uma imagem.")
            return

        nome_arquivo = os.path.basename(self.caminho_imagem)
        destino = os.path.join(PASTA_IMAGENS, nome_arquivo)
        shutil.copy(self.caminho_imagem, destino)

        brinquedo = {
            'nome': nome,
            'tamanho': tamanho,
            'preco': preco,
            'faixa_etaria': faixa,
            'imagem': destino
        }

        brinquedos.append(brinquedo)
        salvar_json(CAMINHO_BRINQUEDOS, brinquedos)
        messagebox.showinfo("Sucesso", "Brinquedo cadastrado com sucesso!")

        self.nome_entry.delete(0, tk.END)
        self.tamanho_entry.delete(0, tk.END)
        self.preco_entry.delete(0, tk.END)
        self.faixa_entry.delete(0, tk.END)
        self.caminho_imagem = None

        self.atualizar_catalogo()
        self.atualizar_lista_brinquedos()

    # =================== USUÁRIO ===================
    def setup_user_tab(self):
        self.catalogo_frame = ttk.Frame(self.user_frame)
        self.catalogo_frame.pack(fill='both', expand=True, side='left')

        self.agendar_frame = ttk.Frame(self.user_frame)
        self.agendar_frame.pack(fill='both', expand=True, side='right')

        # Catálogo
        ttk.Label(self.catalogo_frame, text="Catálogo de Brinquedos", font=('Arial', 14)).pack(pady=10)

        self.lista_catalogo = tk.Canvas(self.catalogo_frame)
        self.scroll_y = ttk.Scrollbar(self.catalogo_frame, orient="vertical", command=self.lista_catalogo.yview)
        self.frame_interno = ttk.Frame(self.lista_catalogo)

        self.frame_interno.bind(
            "<Configure>",
            lambda e: self.lista_catalogo.configure(scrollregion=self.lista_catalogo.bbox("all"))
        )

        self.lista_catalogo.create_window((0, 0), window=self.frame_interno, anchor="nw")
        self.lista_catalogo.configure(yscrollcommand=self.scroll_y.set)

        self.lista_catalogo.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        # Formulário de Agendamento
        ttk.Label(self.agendar_frame, text="Agendar", font=('Arial', 14)).pack(pady=10)

        ttk.Label(self.agendar_frame, text="Nome do Cliente:").pack()
        self.nome_cliente_entry = ttk.Entry(self.agendar_frame)
        self.nome_cliente_entry.pack()

        ttk.Label(self.agendar_frame, text="Telefone:").pack()
        self.telefone_entry = ttk.Entry(self.agendar_frame)
        self.telefone_entry.pack()

        ttk.Label(self.agendar_frame, text="Dia:").pack()
        self.dia_entry = ttk.Entry(self.agendar_frame)
        self.dia_entry.pack()

        ttk.Label(self.agendar_frame, text="Mês:").pack()
        self.mes_entry = ttk.Entry(self.agendar_frame)
        self.mes_entry.pack()

        ttk.Label(self.agendar_frame, text="Ano:").pack()
        self.ano_entry = ttk.Entry(self.agendar_frame)
        self.ano_entry.pack()

        ttk.Label(self.agendar_frame, text="Horário de Início (0-23h):").pack()
        self.horario_entry = ttk.Entry(self.agendar_frame)
        self.horario_entry.pack()

        ttk.Label(self.agendar_frame, text="Selecionar Brinquedos:").pack()
        self.lista_brinquedos = tk.Listbox(self.agendar_frame, selectmode=tk.MULTIPLE, height=6)
        self.lista_brinquedos.pack(pady=5, fill='both', expand=True)
        self.atualizar_lista_brinquedos()

        ttk.Button(self.agendar_frame, text="Calcular Valor", command=self.calcular_valor).pack(pady=10)

        self.valor_label = ttk.Label(self.agendar_frame, text="")
        self.valor_label.pack()

        self.btn_confirmar = ttk.Button(self.agendar_frame, text="Confirmar Agendamento", command=self.realizar_agendamento)
        self.btn_cancelar = ttk.Button(self.agendar_frame, text="Cancelar", command=self.limpar_formulario)

        self.btn_confirmar.pack_forget()
        self.btn_cancelar.pack_forget()

        self.atualizar_catalogo()

    def atualizar_lista_brinquedos(self):
        self.lista_brinquedos.delete(0, tk.END)
        for b in brinquedos:
            self.lista_brinquedos.insert(tk.END, f"{b['nome']} - R$ {b['preco']}")

    def calcular_valor(self):
        selecionados = self.lista_brinquedos.curselection()
        if not selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos um brinquedo.")
            return

        try:
            total = sum(float(brinquedos[i]['preco']) for i in selecionados)
        except:
            messagebox.showerror("Erro", "Erro ao calcular valor. Verifique os preços dos brinquedos.")
            return

        self.valor_total = total
        self.valor_label.config(text=f"Valor Total: R$ {total:.2f}")
        self.btn_confirmar.pack()
        self.btn_cancelar.pack()

    def realizar_agendamento(self):
        nome = self.nome_cliente_entry.get()
        telefone = self.telefone_entry.get()
        dia = self.dia_entry.get()
        mes = self.mes_entry.get()
        ano = self.ano_entry.get()
        horario_inicio = self.horario_entry.get()
        selecionados = self.lista_brinquedos.curselection()

        if not all([nome, telefone, dia, mes, ano, horario_inicio]):
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        if not selecionados:
            messagebox.showerror("Erro", "Selecione pelo menos um brinquedo.")
            return

        try:
            inicio = int(horario_inicio)
            if not (0 <= inicio <= 23):
                raise ValueError
            dia = int(dia)
            mes = int(mes)
            ano = int(ano)
        except ValueError:
            messagebox.showerror("Erro", "Preencha os campos numéricos corretamente.")
            return

        fim = (inicio + 4) % 24

        brinquedos_selecionados = [brinquedos[i]['nome'] for i in selecionados]
        total_valor = sum(float(brinquedos[i]['preco']) for i in selecionados)

        agendamento = {
            'nome': nome,
            'telefone': telefone,
            'dia': dia,
            'mes': mes,
            'ano': ano,
            'inicio': inicio,
            'fim': fim,
            'brinquedos': brinquedos_selecionados,
            'valor_total': total_valor
        }

        agendamentos.append(agendamento)
        salvar_json(CAMINHO_AGENDAMENTOS, agendamentos)

        messagebox.showinfo("Agendamento Confirmado", f"{nome} agendado em {dia}/{mes}/{ano} das {inicio}h às {fim}h.\nTotal: R$ {total_valor:.2f}")

        self.limpar_formulario()
        self.atualizar_lista_agendamentos()
        self.notebook.select(self.agendamento_frame)

    def limpar_formulario(self):
        self.nome_cliente_entry.delete(0, tk.END)
        self.telefone_entry.delete(0, tk.END)
        self.dia_entry.delete(0, tk.END)
        self.mes_entry.delete(0, tk.END)
        self.ano_entry.delete(0, tk.END)
        self.horario_entry.delete(0, tk.END)
        self.lista_brinquedos.selection_clear(0, tk.END)
        self.valor_label.config(text="")
        self.btn_confirmar.pack_forget()
        self.btn_cancelar.pack_forget()

    def atualizar_catalogo(self):
        for widget in self.frame_interno.winfo_children():
            widget.destroy()

        for brinquedo in brinquedos:
            frame = ttk.Frame(self.frame_interno, padding=10, relief='ridge')
            frame.pack(pady=10, fill='x', expand=True)

            try:
                imagem = Image.open(brinquedo['imagem'])
                imagem.thumbnail((100, 100))
                foto = ImageTk.PhotoImage(imagem)
                img_label = tk.Label(frame, image=foto)
                img_label.image = foto
                img_label.pack(side='left', padx=10)
            except:
                pass

            info = (
                f"Nome: {brinquedo['nome']}\n"
                f"Tamanho: {brinquedo['tamanho']}\n"
                f"Preço: R$ {brinquedo['preco']}\n"
                f"Faixa Etária: {brinquedo['faixa_etaria']}"
            )
            tk.Label(frame, text=info, justify='left').pack(anchor='w')

    # =================== AGENDAMENTOS ===================
    def setup_agendamento_tab(self):
        ttk.Label(self.agendamento_frame, text="Agendamentos Realizados", font=('Arial', 14)).pack(pady=10)
        self.lista_agendamentos = tk.Listbox(self.agendamento_frame, height=25)
        self.lista_agendamentos.pack(fill='both', expand=True, padx=20, pady=10)
        self.atualizar_lista_agendamentos()

    def atualizar_lista_agendamentos(self):
        self.lista_agendamentos.delete(0, tk.END)
        for ag in agendamentos:
            data = f"{ag['dia']:02d}/{ag['mes']:02d}/{ag['ano']}"
            brinquedos_txt = ", ".join(ag.get('brinquedos', []))
            item = (
                f"{ag['nome']} - {ag['telefone']} | "
                f"{data} | {ag['inicio']}h às {ag['fim']}h | "
                f"Brinquedos: {brinquedos_txt} | Total: R$ {ag.get('valor_total', 0):.2f}"
            )
            self.lista_agendamentos.insert(tk.END, item)

# Inicia o app
root = tk.Tk()
app = App(root)
root.mainloop()