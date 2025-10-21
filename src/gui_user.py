# gui_user.py
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from storage import salvar_agendamento
from models import Agendamento

class UserTab:
    def __init__(self, parent, brinquedos, agendamentos, atualizar_agendamentos):
        self.frame = ttk.Frame(parent)
        self.brinquedos = brinquedos
        self.agendamentos = agendamentos
        self.atualizar_agendamentos = atualizar_agendamentos
        self.valor_total = 0
        self._montar_interface()

    # ... (funções _montar_interface, atualizar_catalogo, atualizar_lista_brinquedos, calcular_valor são iguais) ...
    def _montar_interface(self):
        # Layout dividido: catálogo e formulário
        self.catalogo_frame = ttk.Frame(self.frame)
        self.catalogo_frame.pack(fill='both', expand=True, side='left')

        self.agendar_frame = ttk.Frame(self.frame)
        self.agendar_frame.pack(fill='both', expand=True, side='right')

        # -------------------- Catálogo --------------------
        ttk.Label(self.catalogo_frame, text="Catálogo de Brinquedos", font=('Arial', 14)).pack(pady=10)

        self.canvas = tk.Canvas(self.catalogo_frame)
        self.scroll_y = ttk.Scrollbar(self.catalogo_frame, orient="vertical", command=self.canvas.yview)
        self.inner_frame = ttk.Frame(self.canvas)

        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll_y.pack(side="right", fill="y")

        # -------------------- Formulário --------------------
        ttk.Label(self.agendar_frame, text="Agendar", font=('Arial', 14)).pack(pady=10)

        campos = [
            ("Nome do Cliente", "nome_cliente_entry"),
            ("Telefone", "telefone_entry"),
            ("Dia", "dia_entry"),
            ("Mês", "mes_entry"),
            ("Ano", "ano_entry"),
            ("Horário de Início (0-23h)", "horario_entry"),
        ]

        for label, attr in campos:
            ttk.Label(self.agendar_frame, text=label + ":").pack()
            entry = ttk.Entry(self.agendar_frame)
            entry.pack()
            setattr(self, attr, entry)

        ttk.Label(self.agendar_frame, text="Selecionar Brinquedos:").pack()
        self.lista_brinquedos = tk.Listbox(self.agendar_frame, selectmode=tk.MULTIPLE, height=6)
        self.lista_brinquedos.pack(pady=5, fill='both', expand=True)

        ttk.Button(self.agendar_frame, text="Calcular Valor", command=self.calcular_valor).pack(pady=10)

        self.valor_label = ttk.Label(self.agendar_frame, text="")
        self.valor_label.pack()

        self.btn_confirmar = ttk.Button(self.agendar_frame, text="Confirmar Agendamento", command=self.realizar_agendamento)
        self.btn_cancelar = ttk.Button(self.agendar_frame, text="Cancelar", command=self.limpar_formulario)
        self.btn_confirmar.pack_forget()
        self.btn_cancelar.pack_forget()

        self.atualizar_catalogo()
        self.atualizar_lista_brinquedos()

    # ---------- Atualização de Catálogo ----------
    def atualizar_catalogo(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        for brinquedo in self.brinquedos:
            frame = ttk.Frame(self.inner_frame, padding=10, relief='ridge')
            frame.pack(pady=10, fill='x', expand=True)

            try:
                imagem = Image.open(brinquedo.imagem)
                imagem.thumbnail((100, 100))
                foto = ImageTk.PhotoImage(imagem)
                img_label = tk.Label(frame, image=foto)
                img_label.image = foto
                img_label.pack(side='left', padx=10)
            except:
                pass

            info = (
                f"Nome: {brinquedo.nome}\n"
                f"Tamanho: {brinquedo.tamanho}\n"
                f"Preço: R$ {brinquedo.preco:.2f}\n"
                f"Faixa Etária: {brinquedo.faixa_etaria}"
            )
            tk.Label(frame, text=info, justify='left').pack(anchor='w')

    def atualizar_lista_brinquedos(self):
        self.lista_brinquedos.delete(0, tk.END)
        for b in self.brinquedos:
            self.lista_brinquedos.insert(tk.END, f"{b.nome} - R$ {b.preco:.2f}")

    # ---------- Agendamento ----------
    def calcular_valor(self):
        selecionados = self.lista_brinquedos.curselection()
        if not selecionados:
            messagebox.showwarning("Aviso", "Selecione pelo menos um brinquedo.")
            return

        try:
            total = sum(float(self.brinquedos[i].preco) for i in selecionados)
        except:
            messagebox.showerror("Erro", "Erro ao calcular valor.")
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
            dia, mes, ano = int(dia), int(mes), int(ano)
            if not (0 <= inicio <= 23):
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Preencha os campos numéricos corretamente.")
            return

        fim = (inicio + 4) % 24
        brinquedos_selecionados = [self.brinquedos[i].nome for i in selecionados]

        agendamento = Agendamento(
            id=None, # <-- 1. PASSAR ID COMO NONE
            nome=nome,
            telefone=telefone,
            dia=dia,
            mes=mes,
            ano=ano,
            inicio=inicio,
            fim=fim,
            brinquedos=brinquedos_selecionados,
            valor_total=self.valor_total
        )

        novo_id = salvar_agendamento(agendamento) # <-- 2. RECEBER O NOVO ID
        agendamento.id = novo_id # <-- 3. ATRIBUIR O ID AO OBJETO
        
        self.agendamentos.append(agendamento)
        
        messagebox.showinfo("Agendamento Confirmado",
                            f"{nome} agendado em {dia}/{mes}/{ano} das {inicio}h às {fim}h.\nTotal: R$ {self.valor_total:.2f}")

        self.limpar_formulario()
        self.atualizar_agendamentos()

    def limpar_formulario(self):
        for campo in [
            self.nome_cliente_entry, self.telefone_entry,
            self.dia_entry, self.mes_entry, self.ano_entry, self.horario_entry
        ]:
            campo.delete(0, tk.END)
        self.lista_brinquedos.selection_clear(0, tk.END)
        self.valor_label.config(text="")
        self.btn_confirmar.pack_forget()
        self.btn_cancelar.pack_forget()