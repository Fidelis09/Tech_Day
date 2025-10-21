# gui_admin.py (versão atualizada)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
from models import Brinquedo
from storage import salvar_brinquedo, atualizar_brinquedo, deletar_brinquedo 

PASTA_IMAGENS = "imagens"
os.makedirs(PASTA_IMAGENS, exist_ok=True)


class AdminTab:
    def __init__(self, parent, brinquedos, atualizar_catalogo, atualizar_lista):
        self.frame = ttk.Frame(parent)
        self.brinquedos = brinquedos
        self.atualizar_catalogo = atualizar_catalogo
        self.atualizar_lista_brinquedos = atualizar_lista
        
        self.caminho_imagem = None
        self.brinquedo_selecionado_id = None # Para saber qual brinquedo estamos editando
        
        self._montar_interface()
        self.atualizar_treeview_brinquedos()

    def _montar_interface(self):
        # Dividir a interface
        self.form_frame = ttk.Frame(self.frame)
        self.form_frame.pack(side='left', fill='y', padx=20, pady=10)

        self.lista_frame = ttk.Frame(self.frame)
        self.lista_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        # --- Formulário (Esquerda) ---
        tk.Label(self.form_frame, text="Gerenciar Brinquedo", font=('Arial', 14)).pack(pady=10)

        tk.Label(self.form_frame, text="Nome do Brinquedo:").pack()
        self.nome_entry = tk.Entry(self.form_frame, width=30)
        self.nome_entry.pack()

        tk.Label(self.form_frame, text="Tamanho (Ex: 5x5m):").pack()
        self.tamanho_entry = tk.Entry(self.form_frame, width=30)
        self.tamanho_entry.pack()

        tk.Label(self.form_frame, text="Preço (R$):").pack()
        self.preco_entry = tk.Entry(self.form_frame, width=30)
        self.preco_entry.pack()

        tk.Label(self.form_frame, text="Faixa etária ideal (Ex: 3-10 anos):").pack()
        self.faixa_entry = tk.Entry(self.form_frame, width=30)
        self.faixa_entry.pack()
        
        self.img_label = tk.Label(self.form_frame, text="Nenhuma imagem selecionada")
        self.img_label.pack(pady=5)

        tk.Button(self.form_frame, text="Selecionar Imagem", command=self.selecionar_imagem).pack(pady=5, fill='x')
        
        # Botões de Ação
        self.btn_cadastrar = tk.Button(self.form_frame, text="Cadastrar Novo Brinquedo", command=self.cadastrar_brinquedo)
        self.btn_cadastrar.pack(pady=10, fill='x')
        
        self.btn_salvar = tk.Button(self.form_frame, text="Salvar Atualização", command=self.salvar_atualizacao, state='disabled')
        self.btn_salvar.pack(pady=5, fill='x')
        
        self.btn_limpar = tk.Button(self.form_frame, text="Limpar Formulário", command=self.limpar_campos)
        self.btn_limpar.pack(pady=5, fill='x')

        # --- Lista (Direita) ---
        tk.Label(self.lista_frame, text="Brinquedos Cadastrados", font=('Arial', 14)).pack(pady=10)

        cols = ('ID', 'Nome', 'Preço', 'Tamanho')
        self.tree = ttk.Treeview(self.lista_frame, columns=cols, show='headings', height=20)
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        
        self.tree.column('Nome', width=200)
        self.tree.column('ID', width=50)

        self.tree.pack(fill='both', expand=True)
        
        self.tree.bind("<<TreeviewSelect>>", self.carregar_brinquedo_para_edicao)
        
        self.btn_deletar = tk.Button(self.lista_frame, text="Deletar Selecionado", command=self.remover_brinquedo)
        self.btn_deletar.pack(pady=10)

    def selecionar_imagem(self):
        caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png *.jpeg")])
        if caminho:
            self.caminho_imagem = caminho
            self.img_label.config(text=os.path.basename(caminho))

    def _copiar_imagem(self):
        if not self.caminho_imagem:
            return None
        destino = os.path.join(PASTA_IMAGENS, os.path.basename(self.caminho_imagem))
        shutil.copy(self.caminho_imagem, destino)
        return destino

    def cadastrar_brinquedo(self):
        nome = self.nome_entry.get()
        tamanho = self.tamanho_entry.get()
        preco_str = self.preco_entry.get()
        faixa = self.faixa_entry.get()

        if not all([nome, tamanho, preco_str, faixa, self.caminho_imagem]):
            messagebox.showerror("Erro", "Preencha todos os campos e selecione uma imagem.")
            return

        try:
            preco = float(preco_str)
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser um número.")
            return

        destino_imagem = self._copiar_imagem()

        brinquedo = Brinquedo(
            id=None, # O ID será gerado pelo banco
            nome=nome,
            tamanho=tamanho,
            preco=preco,
            faixa_etaria=faixa,
            imagem=destino_imagem
        )

        # Salva no DB e obtém o ID
        novo_id = salvar_brinquedo(brinquedo)
        brinquedo.id = novo_id

        # Adiciona na lista local
        self.brinquedos.append(brinquedo)
        
        messagebox.showinfo("Sucesso", "Brinquedo cadastrado com sucesso!")
        
        self.atualizar_tudo()
        self.limpar_campos()

    def salvar_atualizacao(self):
        if self.brinquedo_selecionado_id is None:
            return

        # Encontra o brinquedo na lista local
        brinquedo = next((b for b in self.brinquedos if b.id == self.brinquedo_selecionado_id), None)
        if not brinquedo:
            messagebox.showerror("Erro", "Brinquedo não encontrado.")
            return

        # Pega novos dados do formulário
        brinquedo.nome = self.nome_entry.get()
        brinquedo.tamanho = self.tamanho_entry.get()
        brinquedo.preco = float(self.preco_entry.get())
        brinquedo.faixa_etaria = self.faixa_entry.get()
        
        # Se uma nova imagem foi selecionada, copia e atualiza o caminho
        if self.caminho_imagem:
             brinquedo.imagem = self._copiar_imagem()

        # Salva a atualização no banco de dados
        atualizar_brinquedo(brinquedo)

        messagebox.showinfo("Sucesso", "Brinquedo atualizado com sucesso!")
        self.atualizar_tudo()
        self.limpar_campos()

    def remover_brinquedo(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um brinquedo para deletar.")
            return

        item = self.tree.item(selecionado)
        brinquedo_id = item['values'][0] # Pega o ID da coluna 0

        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir o brinquedo ID {brinquedo_id}?"):
            # Deleta do banco
            deletar_brinquedo(brinquedo_id)

            # Remove da lista local
            self.brinquedos = [b for b in self.brinquedos if b.id != brinquedo_id]

            messagebox.showinfo("Sucesso", "Brinquedo removido.")
            self.atualizar_tudo()
            self.limpar_campos()

    def carregar_brinquedo_para_edicao(self, event=None):
        selecionado = self.tree.selection()
        if not selecionado:
            return

        item = self.tree.item(selecionado)
        brinquedo_id = item['values'][0]

        # Encontra o brinquedo na lista local pelo ID
        brinquedo = next((b for b in self.brinquedos if b.id == brinquedo_id), None)

        if brinquedo:
            self.limpar_campos()
            self.nome_entry.insert(0, brinquedo.nome)
            self.tamanho_entry.insert(0, brinquedo.tamanho)
            self.preco_entry.insert(0, str(brinquedo.preco))
            self.faixa_entry.insert(0, brinquedo.faixa_etaria)
            self.img_label.config(text=os.path.basename(brinquedo.imagem))
            
            # Guarda o ID do brinquedo que está sendo editado
            self.brinquedo_selecionado_id = brinquedo.id
            
            # Habilita/Desabilita botões
            self.btn_salvar.config(state='normal')
            self.btn_cadastrar.config(state='disabled')

    def limpar_campos(self):
        self.nome_entry.delete(0, tk.END)
        self.tamanho_entry.delete(0, tk.END)
        self.preco_entry.delete(0, tk.END)
        self.faixa_entry.delete(0, tk.END)
        
        self.img_label.config(text="Nenhuma imagem selecionada")
        self.caminho_imagem = None
        self.brinquedo_selecionado_id = None
        
        # Reseta botões
        self.btn_salvar.config(state='disabled')
        self.btn_cadastrar.config(state='normal')
        
        # Desseleciona item na treeview
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def atualizar_treeview_brinquedos(self):
        # Limpa a treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Preenche com os dados da lista local
        for b in self.brinquedos:
            self.tree.insert('', tk.END, values=(b.id, b.nome, f"R$ {b.preco:.2f}", b.tamanho))

    def atualizar_tudo(self):
        # Atualiza esta aba
        self.atualizar_treeview_brinquedos()
        # Atualiza as outras abas (Catálogo do Usuário, Lista de Agendamento)
        self.atualizar_catalogo()
        self.atualizar_lista_brinquedos()