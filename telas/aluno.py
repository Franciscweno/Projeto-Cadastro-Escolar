import customtkinter as ctk
from validacoes import validacoes
from tkinter import END
from tkinter import messagebox, ttk
from banco import consultar_alunos, id_existe
from banco import inserir_aluno


class JanelaAluno(ctk.CTkFrame, validacoes):
    def __init__(self, parent, controller: 'App'):
        super().__init__(parent)
        self.controller = controller

        self.tab = ctk.CTkTabview(self)
        self.tab.grid(row= 0, column= 0, padx = 20, sticky= 'nsew')
        self.tab._segmented_button.configure(font= ('IMPACT', 14))
        self.tab.configure(text_color= '#B5B2CA',
                                             segmented_button_selected_color="#4338CA",
                                             segmented_button_unselected_color="#2B2B2B",
                                             segmented_button_selected_hover_color="#5B4AE6")
        self.tab_cadastro = self.tab.add("CADASTRO")
        self.tab_consulta = self.tab.add("CONSULTA")
        self.grid_rowconfigure(0, weight= 1)
        self.grid_columnconfigure(0, weight = 1)

        self.aba_cadastro()
        self.aba_consulta()

    def aba_consulta(self):
        self.frame = ctk.CTkFrame(self.tab_consulta, fg_color="transparent")
        self.frame.grid(row= 0, column= 0, padx=20, pady=20, sticky="nsew")
        self.tab_consulta.grid_rowconfigure(0, weight= 1)
        self.tab_consulta.grid_columnconfigure(0, weight= 1)
        self.grid_rowconfigure(0, weight= 1)
        self.grid_columnconfigure(0, weight = 1)
        self.frame.grid_columnconfigure(0, weight= 0)
        self.frame.grid_columnconfigure(1, weight= 1)

        ctk.CTkLabel(self.frame, text= 'CONSULTAR CADASTRO', font= ('IMPACT', 30), text_color= '#B5B2CA').grid(row= 0, column= 0, columnspan= 4, pady= 20)

        ctk.CTkLabel(self.frame, text="Buscar por:", font= ('IMPACT', 14)).grid(row=1, column=0, padx=10, pady=10)
        self.combo_filtro = ctk.CTkComboBox(self.frame, values=["Nome", "CPF", "ID"],state='readonly', width=100)
        self.combo_filtro.set("Nome")
        self.combo_filtro.grid(row=1, column=1, padx=5,pady= 10, sticky= 'nsew')

        self.entry_busca = ctk.CTkEntry(self.frame, placeholder_text="", width=250)
        self.entry_busca.grid(row=1, column=2, padx=5, pady=10, sticky='nsew')

        self.label_dica_busca = ctk.CTkLabel(self.frame, text="Digite o nome", text_color="#B5B2CA", font=("Arial", 10))
        self.label_dica_busca.grid(row=2, column=2, padx=5, sticky="w")
        self.configurar_validacao_consulta()

        self.btn_buscar = ctk.CTkButton(self.frame, text="🔍", width=40, command=self.consultar_aluno)
        self.btn_buscar.grid(row=1, column=3, padx=5, pady= 10, sticky= 'nsew')

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        self.style.map("Treeview", background=[('selected', '#3498db')])

        self.tree = ttk.Treeview(self.frame, columns=("ID", "Nome", "CPF", "Telefone"), show="headings")
        self.tree.grid(row=3, column=0, columnspan=4, padx=10, pady=20, sticky='nsew')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("CPF", text="CPF")
        self.tree.heading("Telefone", text="Telefone")
        
        self.tree.column("ID", width=40)
        self.tree.column("Nome", width=200)
        self.tree.column("CPF", width=120)
        self.tree.column("Telefone", width=120)

    def consultar_aluno(self):
        try:
            if not self.validar_termo_busca_consulta():
                return

            dados = consultar_alunos(
                self.filtro_busca_consulta(),
                self.termo_busca_consulta()
            )

            self.tratar_resultado_consulta(dados, "aluno")

        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))


        


    def aba_cadastro(self):
        self.frame = ctk.CTkScrollableFrame(self.tab_cadastro, fg_color="transparent")
        self.frame.grid(row= 0, column= 0, padx=20, pady=20, sticky="nsew")
        self.tab_cadastro.grid_rowconfigure(0, weight= 1)
        self.tab_cadastro.grid_columnconfigure(0, weight= 1)
        self.grid_rowconfigure(0, weight= 1)
        self.grid_columnconfigure(0, weight = 1)
        self.frame.grid_columnconfigure(0, weight= 0)
        self.frame.grid_columnconfigure(1, weight= 1)


        ctk.CTkLabel(self.frame, text= 'CADASTRO DE DADOS PESSOAIS DO ALUNO', font= ('IMPACT', 30), text_color= '#B5B2CA').grid(row= 0, column= 0, columnspan= 2, pady= 20)
        
        ctk.CTkLabel(self.frame, text= 'ID_Aluno', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=1, column=0, padx=(10, 5), sticky='ew')
        self.entry_id_aluno = ctk.CTkEntry(self.frame,fg_color="#787879")
        self.entry_id_aluno.grid(row=1, column=1,padx= 5, pady= 10, sticky='w')
        self.entry_id_aluno.insert(0, ' ')
        self.entry_id_aluno.configure(state= 'readonly')

        ctk.CTkLabel(self.frame, text='Digite seu nome completo', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=2, column=0, padx=(10, 5), sticky='ew')
        self.entry_nome = ctk.CTkEntry(self.frame, placeholder_text='Nome completo')
        self.entry_nome.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.entry_nome.bind("<Return>", lambda event: self.validar_nome() and self.entry_data_nasc.focus_set())
        self.nome_erro = ctk.CTkLabel(self.frame, text='', text_color='red')
        self.nome_erro.grid(row=3, column=1, padx=5, pady=5)

        ctk.CTkLabel(self.frame, text='Data de nascimento', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=4, column=0, padx=(10, 5), sticky='ew')
        self.entry_data_nasc = ctk.CTkEntry(self.frame, placeholder_text='DD/MM/AAAA')
        self.entry_data_nasc.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        self.entry_data_nasc.bind('<Return>', lambda event: self.validar_data_nasc() and self.entry_CPF.focus_set())
        self.entry_data_nasc.bind('<KeyRelease>', lambda event: self.formatar_data_digitando(self.entry_data_nasc))
        self.entry_data_nasc.bind('<FocusOut>', lambda event: self.completar_ano_data(self.entry_data_nasc))
        self.erro_data_nasc = ctk.CTkLabel(self.frame, text='', text_color='red')
        self.erro_data_nasc.grid(row=5, column=1, padx=5, pady=5)

        ctk.CTkLabel(self.frame, text='Digite seu CPF', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=6, column=0, padx=(10, 5), sticky='ew')
        self.entry_CPF = ctk.CTkEntry(self.frame, placeholder_text='Digite seu CPF.')
        self.entry_CPF.grid(row=6, column=1, padx=5, pady=5, sticky='ew')
        self.entry_CPF.bind("<Return>", lambda event: self.validar_CPF() and self.entry_CEP.focus_set())
        self.entry_CPF.bind('<KeyRelease>', self.formatar_CPF_digitando)
        self.CPF_erro = ctk.CTkLabel(self.frame, text='', text_color='red')
        self.CPF_erro.grid(row=7, column=1, padx=5, pady=5)

        ctk.CTkLabel(self.frame, text='Digite seu CEP', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=8, column=0, padx=(10, 5), sticky='ew')
        self.entry_CEP = ctk.CTkEntry(self.frame, placeholder_text='00000-000')
        self.entry_CEP.grid(row=8, column=1, padx=5, pady=5, sticky='ew')
        self.entry_CEP.bind('<Return>', lambda event: self.buscar_CEP())
        self.CEP_erro = ctk.CTkLabel(self.frame, text='', text_color='red', font=('Arial', 10))
        self.CEP_erro.grid(row=9, column=1, padx=5, pady=(0, 15))

        ctk.CTkLabel(self.frame, text='Logradouro', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=10, column=0, padx=(10, 5), sticky='ew')
        self.entry_rua = ctk.CTkEntry(self.frame)
        self.entry_rua.grid(row=10, column=1, padx=5, pady=5, sticky='ew')

        ctk.CTkLabel(self.frame, text='Bairro', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=11, column=0, padx=(10, 5), sticky='ew')
        self.entry_bairro = ctk.CTkEntry(self.frame)
        self.entry_bairro.grid(row=11, column=1, padx=5, pady=5, sticky='ew')

        ctk.CTkLabel(self.frame, text='Cidade', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=12, column=0, padx=(10, 5), sticky='ew')
        self.entry_cidade = ctk.CTkEntry(self.frame)
        self.entry_cidade.grid(row=12, column=1, padx=5, pady=5, sticky='ew')

        ctk.CTkLabel(self.frame, text='UF', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=13, column=0, padx=(10, 5), sticky='ew')
        self.combo_uf = ctk.CTkComboBox(self.frame, values=[
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
            'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
            'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ])
        self.combo_uf.configure(state= 'readonly')
        self.combo_uf.grid(row=13, column=1, padx=5, pady=5, sticky='ew')
        self.combo_uf.set('')

        ctk.CTkLabel(self.frame, text='Telefone', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=14, column=0, padx=(10, 5), pady=10, sticky='ew')
        self.entry_telefone = ctk.CTkEntry(self.frame, placeholder_text='Digite seu telefone')
        self.entry_telefone.grid(row=14, column=1, padx=5, pady=5, sticky='ew')
        self.entry_telefone.bind('<Return>', lambda event: self.validar_telefone() and self.entry_email.focus_set())
        self.telefone_erro = ctk.CTkLabel(self.frame, text='', text_color='red')
        self.telefone_erro.grid(row=15, column=1, padx=5, pady=5)

        ctk.CTkLabel(self.frame, text='E-mail', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=16, column=0, padx=(10, 5), sticky='ew')
        self.entry_email = ctk.CTkEntry(self.frame, placeholder_text='Digite seu Email')
        self.entry_email.grid(row=16, column=1, padx=5, pady=5, sticky='ew')
        self.entry_email.bind("<Return>", lambda event: self.validar_Email() and self.combo_sexo.focus_set())
        self.entry_email.bind("<KeyRelease>", self.normalizar_email_digitando)
        self.entry_email.bind("<FocusOut>", lambda event: self.validar_Email())
        self.email_erro = ctk.CTkLabel(self.frame, text='', text_color='red')
        self.email_erro.grid(row=17, column=1, padx=5, pady=5, sticky='ew')

        ctk.CTkLabel(self.frame, text='Sexo', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=18, column=0, padx=(10, 5), sticky='ew')
        self.combo_sexo = ctk.CTkComboBox(self.frame, values=['Selecione', 'Masculino', 'Feminino', 'Outro'])
        self.combo_sexo.grid(row=18, column=1, padx=5, pady=5, sticky='nsew')
        self.combo_sexo.set('Selecione')
        self.combo_sexo.configure(state= 'readonly')
        self.sexo_erro = ctk.CTkLabel(self.frame, text='', text_color='red')
        self.sexo_erro.grid(row=19, column=1, padx=5, pady=5, sticky='ew')

        self.label_sucesso = ctk.CTkLabel(self.frame, text=" ", text_color="green", font=("IMPACT", 28))
        self.label_sucesso.grid(row=20, column=0, columnspan=2, pady=5, padx=20)
        self.label_sucesso.configure(text= ' ')

        ctk.CTkButton(
            self.frame,
            text='CONFIRMAR DADOS PESSOAIS',
            font=('IMPACT', 20),
            text_color="#B5B2CA",
            command=self.confirmar_cadastro
        ).grid(row=21, column=0, padx=10, pady=30, sticky='ew')

        ctk.CTkButton(
            self.frame,
            text='LIMPAR CAMPOS',
            font=('IMPACT', 20),
            text_color="#B5B2CA",
            command=self.fechar_e_limpar
        ).grid(row=21, column=1, padx=10, pady=30, sticky='ew')

    def mostrar_sucesso(self):
        self.label_sucesso.configure(text="Cadastro realizado com sucesso!")
        self.after(3000, self.esconder_sucesso)

    def esconder_sucesso(self):
        self.label_sucesso.configure(text= ' ')

    def confirmar_cadastro(self):
        if not self.main_validacoes():
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos")
            return False

        dados = {
        "nome": self.entry_nome.get().strip(),
        "data_nasc": self.entry_data_nasc.get().strip(),
        "cpf": self.entry_CPF.get().strip(),
        "cep": self.entry_CEP.get().strip(),
        "rua": self.entry_rua.get().strip(),
        "bairro": self.entry_bairro.get().strip(),
        "cidade": self.entry_cidade.get().strip(),
        "uf": self.combo_uf.get().strip(),
        "telefone": self.entry_telefone.get().strip(),
        "email": self.entry_email.get().strip().lower(),
        "sexo": self.combo_sexo.get().strip()
    }

        try:
            novo_id = inserir_aluno(dados)

            self.entry_id_aluno.configure(state="normal")
            self.entry_id_aluno.delete(0, END)
            self.entry_id_aluno.insert(0, str(novo_id))
            self.entry_id_aluno.configure(state="readonly")

            self.mostrar_sucesso()
            self.limpar_formulario()

        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
            return False

    def limpar_formulario(self):
        self.entry_nome.delete(0, END)
        self.entry_CEP.delete(0, END)
        self.entry_rua.delete(0, END)
        self.entry_bairro.delete(0, END)
        self.entry_cidade.delete(0, END)
        self.entry_CPF.delete(0, END)
        self.entry_telefone.delete(0, END)
        self.entry_email.delete(0, END)
        self.entry_data_nasc.delete(0, END)

        self.combo_uf.set('')
        self.combo_sexo.set('Selecione')

        self.CEP_erro.configure(text='')

    def fechar_e_limpar(self):
        self.limpar_formulario() 

    def preencher_tree(self, dados):
        self.tree.delete(*self.tree.get_children())
        for linha in dados:
            self.tree.insert("", "end", values=linha)
