# main.py
import tkinter as tk
from tkinter import ttk
from storage import carregar_brinquedos, carregar_agendamentos, inicializar_banco
from gui_admin import AdminTab
from gui_user import UserTab
from gui_agendamento import AgendamentoTab

class App:
    def __init__(self, root):

        inicializar_banco()
        
        self.root = root
    
        self.root.title("Sistema de Brinquedos Infláveis")
        self.root.geometry("1000x650")

        self.brinquedos = carregar_brinquedos()
        self.agendamentos = carregar_agendamentos()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both')

        # Abas
        self.user_tab = UserTab(self.notebook, self.brinquedos, self.agendamentos, self.atualizar_agendamentos)
        self.admin_tab = AdminTab(self.notebook, self.brinquedos, self.user_tab.atualizar_catalogo, self.user_tab.atualizar_lista_brinquedos)
        self.agendamento_tab = AgendamentoTab(self.notebook, self.agendamentos)

        self.notebook.add(self.user_tab.frame, text="Usuário")
        self.notebook.add(self.admin_tab.frame, text="Admin")
        self.notebook.add(self.agendamento_tab.frame, text="Agendamentos")

    def atualizar_agendamentos(self):
        self.agendamento_tab.atualizar_lista()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
