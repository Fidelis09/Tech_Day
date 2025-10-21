# gui_agendamento.py
import tkinter as tk
from tkinter import ttk, messagebox  # <-- 1. IMPORTAR MESSAGEBOX
from storage import deletar_agendamento # <-- 2. IMPORTAR FUNÇÃO DELETAR

class AgendamentoTab:
    def __init__(self, parent, agendamentos):
        self.frame = ttk.Frame(parent)
        self.agendamentos = agendamentos
        self._montar_interface()

    def _montar_interface(self):
        ttk.Label(self.frame, text="Agendamentos Realizados", font=('Arial', 14)).pack(pady=10)
        
        self.lista = tk.Listbox(self.frame, height=25)
        self.lista.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 3. ADICIONAR BOTÃO DE EXCLUIR
        self.btn_deletar = ttk.Button(self.frame, text="Excluir Agendamento Selecionado", command=self.excluir_agendamento)
        self.btn_deletar.pack(pady=10)
        
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

    # 4. NOVA FUNÇÃO PARA EXCLUIR
    def excluir_agendamento(self):
        selecionado = self.lista.curselection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um agendamento para excluir.")
            return

        # O índice da listbox é o mesmo da nossa lista self.agendamentos
        indice_selecionado = selecionado[0]
        
        ag_para_excluir = self.agendamentos[indice_selecionado]
        
        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir o agendamento de '{ag_para_excluir.nome}' do dia {ag_para_excluir.dia}/{ag_para_excluir.mes}?"):
            
            # 1. Deletar do banco de dados usando o ID
            deletar_agendamento(ag_para_excluir.id)
            
            # 2. Remover da lista local (que é compartilhada com main.py)
            self.agendamentos.pop(indice_selecionado)
            
            # 3. Atualizar a interface (a listbox)
            self.atualizar_lista()
            
            messagebox.showinfo("Sucesso", "Agendamento excluído.")