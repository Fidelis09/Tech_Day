# gui_agendamento.py
import tkinter as tk
from tkinter import ttk

class AgendamentoTab:
    def __init__(self, parent, agendamentos):
        self.frame = ttk.Frame(parent)
        self.agendamentos = agendamentos
        self._montar_interface()

    def _montar_interface(self):
        ttk.Label(self.frame, text="Agendamentos Realizados", font=('Arial', 14)).pack(pady=10)
        self.lista = tk.Listbox(self.frame, height=25)
        self.lista.pack(fill='both', expand=True, padx=20, pady=10)
        self.atualizar_lista()

    def atualizar_lista(self):
        self.lista.delete(0, tk.END)
        for ag in self.agendamentos:
            data = f"{ag.dia:02d}/{ag.mes:02d}/{ag.ano}"
            brinquedos_txt = ", ".join(ag.brinquedos)
            item = (
                f"{ag.nome} - {ag.telefone} | "
                f"{data} | {ag.inicio}h às {ag.fim}h | "
                f"Brinquedos: {brinquedos_txt} | Total: R$ {ag.valor_total:.2f}"
            )
            self.lista.insert(tk.END, item)
