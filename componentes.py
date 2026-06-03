import customtkinter as ctk
from tkinter import END
from tkinter import messagebox

from validacoes import validacoes


class frame_baseAlunoProf(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=0)
        parent.columnconfigure(2, weight=1)

        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=0)
        parent.rowconfigure(2, weight=1)

        self.grid(row=1, column=1, pady=10, padx=30, sticky='n')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        for i in range(18):
            self.rowconfigure(i, weight=1)


class componentes_reutilizaveis(ctk.CTkScrollableFrame, validacoes):
    def __init__(self, parent, tipo='aluno'):
        super().__init__(parent)
        self.tipo = tipo

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text='Digite seu nome completo', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=0, column=0, padx=(10, 5), sticky='ew')
        self.entry_nome = ctk.CTkEntry(self, placeholder_text='Nome completo')
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.entry_nome.bind("<Return>", lambda event: self.validar_nome() and self.entry_CPF.focus_set())
        self.nome_erro = ctk.CTkLabel(self, text='', text_color='red')
        self.nome_erro.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(self, text='Digite seu CPF', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=2, column=0, padx=(10, 5), sticky='ew')
        self.entry_CPF = ctk.CTkEntry(self, placeholder_text='Digite seu CPF.')
        self.entry_CPF.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.entry_CPF.bind("<Return>", lambda event: self.validar_CPF() and self.entry_CEP.focus_set())
        self.CPF_erro = ctk.CTkLabel(self, text='', text_color='red')
        self.CPF_erro.grid(row=3, column=1, padx=5, pady=5)

        ctk.CTkLabel(self, text='Digite seu CEP', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=4, column=0, padx=(10, 5), sticky='ew')
        self.entry_CEP = ctk.CTkEntry(self, placeholder_text='00000-000')
        self.entry_CEP.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        self.entry_CEP.bind('<Return>', lambda event: self.buscar_CEP())
        self.CEP_erro = ctk.CTkLabel(self, text='', text_color='red', font=('Arial', 10))
        self.CEP_erro.grid(row=5, column=1, padx=5, pady=(0, 15))

        ctk.CTkLabel(self, text='Logradouro', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=6, column=0, padx=(10, 5), sticky='ew')
        self.entry_rua = ctk.CTkEntry(self)
        self.entry_rua.grid(row=6, column=1, padx=5, pady=5, sticky='ew')

        ctk.CTkLabel(self, text='Bairro', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=7, column=0, padx=(10, 5), sticky='ew')
        self.entry_bairro = ctk.CTkEntry(self)
        self.entry_bairro.grid(row=7, column=1, padx=5, pady=5, sticky='ew')

        ctk.CTkLabel(self, text='Cidade', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=8, column=0, padx=(10, 5), sticky='ew')
        self.entry_cidade = ctk.CTkEntry(self)
        self.entry_cidade.grid(row=8, column=1, padx=5, pady=5, sticky='ew')

        ctk.CTkLabel(self, text='UF', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=9, column=0, padx=(10, 5), sticky='ew')
        self.combo_uf = ctk.CTkComboBox(self, values=[
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ])
        self.combo_uf.grid(row=9, column=1, padx=5, pady=5, sticky='ew')
        self.combo_uf.set('')

        ctk.CTkLabel(self, text='Telefone', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=10, column=0, padx=(10, 5), pady=10, sticky='ew')
        self.entry_telefone = ctk.CTkEntry(self, placeholder_text='Digite seu telefone')
        self.entry_telefone.grid(row=10, column=1, padx=5, pady=5, sticky='ew')
        self.entry_telefone.bind('<Return>', lambda event: self.validar_telefone() and self.entry_email.focus_set())
        self.telefone_erro = ctk.CTkLabel(self, text='', text_color='red')
        self.telefone_erro.grid(row=11, column=1, padx=5, pady=5)

        ctk.CTkLabel(self, text='E-mail', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=12, column=0, padx=(10, 5), sticky='ew')
        self.entry_email = ctk.CTkEntry(self, placeholder_text='Digite seu Email')
        self.entry_email.grid(row=12, column=1, padx=5, pady=5, sticky='ew')
        self.entry_email.bind("<Return>", lambda event: self.validar_Email() and self.combo_sexo.focus_set())
        self.email_erro = ctk.CTkLabel(self, text='', text_color='red')
        self.email_erro.grid(row=13, column=1, padx=5, pady=5, sticky='ew')

        ctk.CTkLabel(self, text='Sexo', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=14, column=0, padx=(10, 5), sticky='ew')
        self.combo_sexo = ctk.CTkComboBox(self, values=['Selecione', 'Masculino', 'Feminino', 'Outro'])
        self.combo_sexo.grid(row=14, column=1, padx=5, pady=5, sticky='nsew')
        self.combo_sexo.set('Selecione')
        self.sexo_erro = ctk.CTkLabel(self, text='', text_color='red')
        self.sexo_erro.grid(row=15, column=1, padx=5, pady=5, sticky='ew')

        self.label_sucesso = ctk.CTkLabel(self, text="Cadastro realizado com sucesso!", text_color="green", font=("IMPACT", 22))
        self.label_sucesso.grid(row=16, column=0, columnspan=2, pady=5, padx=20)
        self.label_sucesso.grid_remove()

        ctk.CTkButton(
            self,
            text='CONFIRMAR DADOS PESSOAIS',
            font=('IMPACT', 20),
            text_color="#B5B2CA",
            command=self.confirmar_cadastro
        ).grid(row=17, column=0, padx=10, pady=30, sticky='ew')

        ctk.CTkButton(
            self,
            text='LIMPAR CAMPOS',
            font=('IMPACT', 20),
            text_color="#B5B2CA",
            command=self.fechar_e_limpar
        ).grid(row=17, column=1, padx=10, pady=30, sticky='ew')

    def mostrar_sucesso(self):
        self.label_sucesso.configure(text="Cadastro realizado com sucesso!")
        self.label_sucesso.grid()
        self.after(3000, self.esconder_sucesso)

    def esconder_sucesso(self):
        self.label_sucesso.grid_remove()

    def confirmar_cadastro(self):
        if not self.main_validacoes():
            messagebox.showerror('Erro', 'Todos os campos devem ser preenchidos')
            return

        if self.tipo == 'professor':
            from telas.dados_acad_prof import Dados_acad_prof
            self.top = Dados_acad_prof(self, self)
            return

        self.mostrar_sucesso()
        self.limpar_formulario()

    def limpar_formulario(self):
        self.entry_nome.delete(0, END)
        self.entry_CEP.delete(0, END)
        self.entry_rua.delete(0, END)
        self.entry_bairro.delete(0, END)
        self.entry_cidade.delete(0, END)
        self.entry_CPF.delete(0, END)
        self.entry_telefone.delete(0, END)
        self.entry_email.delete(0, END)

        self.combo_uf.set('')
        self.combo_sexo.set('Selecione')

        self.CEP_erro.configure(text='')

    def fechar_e_limpar(self):
        self.limpar_formulario()
