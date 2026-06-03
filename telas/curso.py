import customtkinter as ctk
from tkinter import END,ttk, messagebox
from validacoes import validacoes
from banco import consultar_cursos, id_existe, inserir_curso


class JanelaCurso(ctk.CTkFrame, validacoes):
    def __init__(self, parent, controller):
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

        self.aba_curso()
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

        ctk.CTkLabel(self.frame, text= 'CONSULTAR CURSO', font= ('IMPACT', 30), text_color= '#B5B2CA').grid(row= 0, column= 0, columnspan= 4, pady= 20)

        ctk.CTkLabel(self.frame, text="Buscar por:", font= ('IMPACT', 14)).grid(row=1, column=0, padx=10, pady=10)
        self.combo_filtro = ctk.CTkComboBox(self.frame, values=['ID', "Nome do curso", 'Turma', 'Aluno',],state='readonly', width=100)
        self.combo_filtro.set("ID")
        self.combo_filtro.grid(row=1, column=1, padx=5,pady= 10, sticky= 'nsew')

        self.entry_busca = ctk.CTkEntry(self.frame, placeholder_text="", width=250)
        self.entry_busca.grid(row=1, column=2, padx=5, pady=10, sticky='nsew')

        self.label_dica_busca = ctk.CTkLabel(self.frame, text="Digite apenas números", text_color="#B5B2CA", font=("Arial", 10))
        self.label_dica_busca.grid(row=2, column=2, padx=5, sticky="w")
        self.configurar_validacao_consulta()

        self.btn_buscar = ctk.CTkButton(self.frame, text="🔍", width=40, command=self.consultar_curso)
        self.btn_buscar.grid(row=1, column=3, padx=5, pady= 10, sticky= 'nsew')

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        self.style.map("Treeview", background=[('selected', '#3498db')])

        self.tree = ttk.Treeview(self.frame, columns=("ID", "Nome do curso", 'Turmas', "Alunos Matriculados"), show="headings")
        self.tree.grid(row=3, column=0, columnspan=4, padx=10, pady=20, sticky='nsew')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome do curso", text="Nome do curso")
        self.tree.heading("Turmas", text="Turmas")
        self.tree.heading("Alunos Matriculados", text="Alunos Matriculados")
        
        
        self.tree.column("ID", width=50)
        self.tree.column("Nome do curso", width=150)
        self.tree.column("Turmas", width=50)
        self.tree.column("Alunos Matriculados", width=150)

    def consultar_curso(self):
        try:
            if not self.validar_termo_busca_consulta():
                return

            dados = consultar_cursos(
                self.filtro_busca_consulta(),
                self.termo_busca_consulta()
            )

            self.tratar_resultado_consulta(dados, "curso")

        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
        
    def aba_curso(self):
        self.frame = ctk.CTkFrame(self.tab_cadastro)
        self.frame.grid(row= 0, column= 0, padx=20, pady=20, sticky="nsew")
        self.tab_cadastro.grid_rowconfigure(0, weight= 0)
        self.tab_cadastro.grid_columnconfigure(0, weight= 1)
        self.grid_rowconfigure(0, weight= 1)
        self.grid_columnconfigure(0, weight = 1)
        self.frame.grid_columnconfigure(0, weight= 0)
        self.frame.grid_columnconfigure(1, weight= 1)

        self.frame.grid_rowconfigure(8, weight= 1)

        ctk.CTkLabel(self.frame, text= 'CADASTRO DE CURSO', font= ('IMPACT', 30), text_color="#B5B2CA").grid(row= 0, column= 0, columnspan= 2, pady= 10)
        
        
        ctk.CTkLabel(self.frame, text= 'ID_Curso', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        self.entry_id = ctk.CTkEntry(self.frame, fg_color= "#6B6B6B")
        self.entry_id.grid(row= 1, column= 1, padx=10, pady=10, sticky='w')
        self.entry_id.insert(0, ' ')
        self.entry_id.configure(state= 'readonly')

        ctk.CTkLabel(self.frame, text= 'Nome do Curso', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        self.entry_curso = ctk.CTkEntry(self.frame, placeholder_text='Ex: Banco de Dados')
        self.entry_curso.grid(row= 2, column= 1, padx=10, pady=10, sticky='ew')
        self.entry_curso.bind('<Return>', lambda event: self.validar_curso() and self.entry_carga_horaria.focus_set())
        self.label_erro_curso = ctk.CTkLabel(self.frame, text= '', text_color= 'red')
        self.label_erro_curso.grid(row= 3, column= 1,pady= 5, sticky= 'new')

        self.label_sucesso_curso = ctk.CTkLabel(self.frame, text= '', text_color="green", font=("IMPACT", 28))
        self.label_sucesso_curso.grid(row= 6, column= 0,columnspan= 2, padx= 10)
        self.label_sucesso_curso.grid_remove()

        ctk.CTkLabel(self.frame, text= 'Carga horária', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=4 ,column= 0, padx=10, pady=10, sticky='ew')
        self.entry_carga_horaria = ctk.CTkEntry(self.frame, placeholder_text='Carga horária do curso')
        self.entry_carga_horaria.grid(row= 4, column= 1, padx=10, pady=10, sticky='ew')
        self.entry_carga_horaria.bind('<Return>', lambda event: self.cadastrar_curso())
        self.erro_carga_horaria = ctk.CTkLabel(self.frame, text= '', text_color= 'red')
        self.erro_carga_horaria.grid(row= 5, column= 1, padx= 10, sticky= 'ew')

        ctk.CTkButton(self.frame,
                      text= 'CADASTRAR CURSO',
                      font=('IMPACT', 20),
                      text_color= "#B5B2CA",
                      command=self.cadastrar_curso).grid(row= 7, column= 0, padx= 10, sticky= 'ew')
        ctk.CTkButton(self.frame,
                      text= 'LIMPAR CAMPO',
                      font=('IMPACT', 20),
                      text_color= "#B5B2CA",
                      command= self.limpar_curso).grid(row= 7, column= 1, padx= 10, sticky= 'ew')
        
    def cadastrar_curso(self):
        if not self.validar_curso() or not self.validar_carga_horaria():
            messagebox.showerror("Erro", "Preencha os campos corretamente.")
            return False

        dados = {
        "nome_curso": self.entry_curso.get().strip(),
        "carga_horaria": self.entry_carga_horaria.get().strip()
    }

        try:
            novo_id = inserir_curso(dados)

            self.entry_id.configure(state="normal")
            self.entry_id.delete(0, END)
            self.entry_id.insert(0, str(novo_id))
            self.entry_id.configure(state="readonly")

            self.winfo_toplevel().event_generate("<<CursoCadastrado>>", when="tail")

            self.label_sucesso_curso.configure(text="Curso cadastrado com sucesso!")
            self.label_sucesso_curso.grid()
            self.after(3000, self.esconder_sucesso)
            return True

        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
        return False

    def esconder_sucesso(self):
        self.label_sucesso_curso.grid_remove()
        self.limpar_curso()

    def limpar_curso(self):
        self.entry_curso.delete(0, END)
        self.entry_carga_horaria.delete(0, END)

    def preencher_tree(self, dados):
        self.tree.delete(*self.tree.get_children())
        for linha in dados:
            self.tree.insert("", "end", values=linha)