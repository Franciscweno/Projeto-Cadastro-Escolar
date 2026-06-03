import customtkinter as ctk
from tkinter import messagebox, END
from validacoes import validacoes
from banco import inserir_professor_com_academico


class Dados_acad_prof(ctk.CTkToplevel, validacoes):
    def __init__(self, parent, campos):
        super().__init__(parent)

        self.campos = campos

        largura = 620
        altura = 690
        x = 600
        y = 95

        self.geometry(f"{largura}x{altura}+{x}+{y}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.lift()
        self.focus()

        self.grid_columnconfigure(0, weight=0, minsize=210)
        self.grid_columnconfigure(1, weight=1, minsize=320)

        for i in range(12):
            self.grid_rowconfigure(i, weight=0)

        ctk.CTkLabel(
            self,
            text='DADOS ACADÊMICOS',
            font=('IMPACT', 22),
            text_color='#9692BB'
        ).grid(row=0, column=0, columnspan=2, pady=(15, 20), sticky='ew')

        ctk.CTkLabel(self, text='Instituição Educacional', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=1, column=0, padx=(15, 10), pady=(6, 6), sticky='w')
        self.entry_inst = ctk.CTkEntry(self, placeholder_text='Digite a IE aqui')
        self.entry_inst.grid(row=1, column=1, padx=(10, 15), pady=(6, 6), sticky='ew')
        self.entry_inst.bind('<Return>', lambda event: self.validar_inst() and self.entry_curso.focus_set())
        self.erro_inst = ctk.CTkLabel(self, text='', text_color='red')
        self.erro_inst.grid(row=2, column=1, padx=(10, 15), pady=(0, 6), sticky='w')

        ctk.CTkLabel(self, text='Curso', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=3, column=0, padx=(15, 10), pady=(6, 6), sticky='w')
        self.entry_curso = ctk.CTkEntry(self, placeholder_text='Digite o curso')
        self.entry_curso.grid(row=3, column=1, padx=(10, 15), pady=(6, 6), sticky='ew')
        self.entry_curso.bind('<Return>', lambda event: self.validar_curso() and self.combo_grau.focus_set())
        self.label_erro_curso = ctk.CTkLabel(self, text='', text_color='red')
        self.label_erro_curso.grid(row=4, column=1, padx=(10, 15), pady=(0, 6), sticky='w')

        ctk.CTkLabel(self, text='Grau', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=5, column=0, padx=(15, 10), pady=(6, 6), sticky='w')
        self.combo_grau = ctk.CTkComboBox(self, values=['Grau', 'Graduação', 'Especialização', 'Mestrado', 'Doutorado', 'Pós-Doutorado'])
        self.combo_grau.grid(row=5, column=1, padx=(10, 15), pady=(6, 6), sticky='ew')
        self.combo_grau.set('Grau')
        self.combo_grau.configure(state= 'readonly')
        self.erro_grau = ctk.CTkLabel(self, text='', text_color='red')
        self.erro_grau.grid(row=6, column=1, padx=(10, 15), pady=(0, 6), sticky='w')

        ctk.CTkLabel(self, text='Início do curso (dd/mm/aaaa)', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=7, column=0, padx=(15, 10), pady=(6, 6), sticky='w')
        self.entry_data_inicio = ctk.CTkEntry(self, placeholder_text='DD/MM/AAAA')
        self.entry_data_inicio.grid(row=7, column=1, padx=(10, 15), pady=(6, 6), sticky='ew')
        self.entry_data_inicio.bind('<Return>', lambda event: self.validar_data_inicio() and self.entry_data_fim.focus_set())
        self.entry_data_inicio.bind('<KeyRelease>', lambda event: self.formatar_data_digitando(self.entry_data_inicio))
        self.entry_data_inicio.bind('<FocusOut>', lambda event: self.completar_ano_data(self.entry_data_inicio))
        self.erro_dt_inicio = ctk.CTkLabel(self, text='', text_color='red')
        self.erro_dt_inicio.grid(row=8, column=1, padx=(10, 15), pady=(0, 6), sticky='w')

        ctk.CTkLabel(self, text='Fim do curso (dd/mm/aaaa)', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=9, column=0, padx=(15, 10), pady=(6, 6), sticky='w')
        self.entry_data_fim = ctk.CTkEntry(self, placeholder_text='DD/MM/AAAA')
        self.entry_data_fim.grid(row=9, column=1, padx=(10, 15), pady=(6, 6), sticky='ew')
        self.entry_data_fim.bind('<Return>', lambda event: self.validar_data_fim() and self.cadastrar())
        self.entry_data_fim.bind('<KeyRelease>', lambda event: self.formatar_data_digitando(self.entry_data_fim))
        self.entry_data_fim.bind('<FocusOut>', lambda event: self.completar_ano_data(self.entry_data_fim))
        self.erro_dt_fim = ctk.CTkLabel(self, text='', text_color='red')
        self.erro_dt_fim.grid(row=10, column=1, padx=(10, 15), pady=(0, 10), sticky='w')

        ctk.CTkButton(self, text='CADASTRAR', font=('IMPACT', 20), text_color="#B5B2CA", command=self.cadastrar).grid(row=11, column=0, padx=(15, 8), pady=(15, 20), sticky='ew')
        ctk.CTkButton(self, text='VOLTAR', font=('IMPACT', 20), text_color="#B5B2CA", command=self.destroy).grid(row=11, column=1, padx=(8, 15), pady=(15, 20), sticky='ew')

    def cadastrar(self):
        if not self.validacoes_dados_acad():
            messagebox.showerror("Erro", "Preencha os dados acadêmicos corretamente.")
            return False

        dados_professor = {
        "nome": self.campos.entry_nome.get().strip(),
        "data_nasc": self.campos.entry_data_nasc.get().strip(),
        "cpf": self.campos.entry_CPF.get().strip(),
        "cep": self.campos.entry_CEP.get().strip(),
        "rua": self.campos.entry_rua.get().strip(),
        "bairro": self.campos.entry_bairro.get().strip(),
        "cidade": self.campos.entry_cidade.get().strip(),
        "uf": self.campos.combo_uf.get().strip(),
        "telefone": self.campos.entry_telefone.get().strip(),
        "email": self.campos.entry_email.get().strip().lower(),
        "sexo": self.campos.combo_sexo.get().strip()
    }

        dados_acad = {
        "instituicao": self.entry_inst.get().strip(),
        "curso": self.entry_curso.get().strip(),
        "grau": self.combo_grau.get().strip(),
        "data_inicio": self.entry_data_inicio.get().strip(),
        "data_fim": self.entry_data_fim.get().strip()
    }

        try:
            novo_id = inserir_professor_com_academico(dados_professor, dados_acad)

            self.campos.entry_id_prof.configure(state="normal")
            self.campos.entry_id_prof.delete(0, END)
            self.campos.entry_id_prof.insert(0, str(novo_id))
            self.campos.entry_id_prof.configure(state="readonly")

            messagebox.showinfo("Cadastro Acadêmico", "Professor cadastrado com sucesso.")
            self.campos.mostrar_sucesso()
            self.campos.limpar_formulario()
            self.destroy()

        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
            return False
