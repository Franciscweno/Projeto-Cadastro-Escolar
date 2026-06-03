import customtkinter as ctk
from tkinter import END,ttk,messagebox
from validacoes import validacoes
from banco import consultar_disciplinas, id_existe, inserir_disciplina, listar_cursos_combo



class JanelaDisciplina(ctk.CTkFrame, validacoes):
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

        self.aba_disciplina()
        self.aba_consulta()

        self.winfo_toplevel().bind(
            "<<CursoCadastrado>>",
            self.atualizar_combo_cursos_disciplina,
            add="+"
        )

    def aba_consulta(self):
        self.frame = ctk.CTkFrame(self.tab_consulta, fg_color="transparent")
        self.frame.grid(row= 0, column= 0, padx=20, pady=20, sticky="nsew")
        self.tab_consulta.grid_rowconfigure(0, weight= 1)
        self.tab_consulta.grid_columnconfigure(0, weight= 1)
        self.grid_rowconfigure(0, weight= 1)
        self.grid_columnconfigure(0, weight = 1)
        self.frame.grid_columnconfigure(0, weight= 0)
        self.frame.grid_columnconfigure(1, weight= 1)

        ctk.CTkLabel(self.frame, text= 'CONSULTAR DISCIPLINA', font= ('IMPACT', 30), text_color= '#B5B2CA').grid(row= 0, column= 0, columnspan= 4, pady= 20)

        ctk.CTkLabel(self.frame, text="Buscar por:", font= ('IMPACT', 14)).grid(row=1, column=0, padx=10, pady=10)
        self.combo_filtro = ctk.CTkComboBox(self.frame, values=["Nome da Disciplina", "ID", 'Professor'],state='readonly', width=100)
        self.combo_filtro.set("Nome da Disciplina")
        self.combo_filtro.grid(row=1, column=1, padx=5,pady= 10, sticky= 'nsew')

        self.entry_busca = ctk.CTkEntry(self.frame, placeholder_text="", width=250)
        self.entry_busca.grid(row=1, column=2, padx=5, pady=10, sticky='nsew')

        self.label_dica_busca = ctk.CTkLabel(self.frame, text="Digite sua consulta", text_color="#B5B2CA", font=("Arial", 10))
        self.label_dica_busca.grid(row=2, column=2, padx=5, sticky="w")
        self.configurar_validacao_consulta()

        self.btn_buscar = ctk.CTkButton(self.frame, text="🔍", width=40, command=self.consultar_disciplina)
        self.btn_buscar.grid(row=1, column=3, padx=5, pady= 10, sticky= 'nsew')

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        self.style.map("Treeview", background=[('selected', '#3498db')])

        self.tree = ttk.Treeview(self.frame, columns=("ID", "Disciplina", 'Cursos', "Professor"), show="headings")
        self.tree.grid(row=3, column=0, columnspan=4, padx=10, pady=20, sticky='nsew')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Disciplina", text="Disciplina")
        self.tree.heading("Cursos", text="Cursos")
        self.tree.heading("Professor", text="Professor")
        self.tree.column("Cursos", width=200)
        
        self.tree.column("ID", width=40)
        self.tree.column("Disciplina", width=200)
        self.tree.column("Cursos", width=200)
        self.tree.column("Professor", width=200)

    def consultar_disciplina(self):
        try:
            if not self.validar_termo_busca_consulta():
                return

            dados = consultar_disciplinas(
                self.filtro_busca_consulta(),
                self.termo_busca_consulta()
            )

            self.tratar_resultado_consulta(dados, "disciplina")

        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))    

    def aba_disciplina(self):

        #FRAME CENTRALIZADO
        self.frame = ctk.CTkFrame(self.tab_cadastro)
        self.frame.grid(row= 0, column= 0, padx=20, pady=20, sticky="nsew")
        self.tab_cadastro.grid_rowconfigure(0, weight= 0)
        self.tab_cadastro.grid_columnconfigure(0, weight= 1)
        self.grid_rowconfigure(0, weight= 1)
        self.grid_columnconfigure(0, weight = 1)
        self.frame.grid_columnconfigure(0, weight= 1)
        self.frame.grid_columnconfigure(1, weight= 1)

        self.frame.grid_rowconfigure(8, weight= 1)

        ctk.CTkLabel(self.frame, text= 'CADASTRO DE DISCIPLINA', font= ('IMPACT', 30), text_color= '#B5B2CA').grid(row= 0, column= 0, columnspan= 2, pady= 20)

        ctk.CTkLabel(self.frame, text="Nome da Disciplina", font=('IMPACT', 14), text_color="#B5B2CA").grid(row=3, column=0, padx=10, pady=10, sticky='w')
        self.entry_disciplina = ctk.CTkEntry(self.frame, placeholder_text='Digite o nome da Disciplina')
        self.entry_disciplina.grid(row=3, column=1, padx=(10, 5), sticky='ew')
        self.entry_disciplina.bind('<Return>', lambda event: self.validar_disciplina() and self.entry_num_disc.focus_set())
        self.erro_NomeDisc = ctk.CTkLabel(self.frame, text='', text_color='red')
        self.erro_NomeDisc.grid(row=4, column=1, padx=(10, 5), sticky='w')

        ctk.CTkLabel(self.frame, text='ID da Disciplina', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.entry_num_disc = ctk.CTkEntry(self.frame, placeholder_text='Número da Disciplina', fg_color="#787879")
        self.entry_num_disc.grid(row=1, column=1, padx=(10, 5), sticky='W')
        self.entry_num_disc.insert(0, ' ')
        self.entry_num_disc.configure(state= 'readonly')

        ctk.CTkLabel(
            self.frame,
            text='Curso',
            font=('IMPACT', 14),
            text_color="#B5B2CA"
        ).grid(row=5, column=0, padx=10, pady=10, sticky='w')

        self.combo_curso_disc = ctk.CTkComboBox(
            self.frame,
            values=["Carregando cursos..."],
            state="readonly",
            width=260
        )
        self.combo_curso_disc.grid(row=5, column=1, padx=(10, 5), sticky='w')
        self.combo_curso_disc.set("Selecione um curso")

        self.erro_id_curso_disc = ctk.CTkLabel(
            self.frame,
            text='',
            text_color='red'
        )
        self.erro_id_curso_disc.grid(row=6, column=1, padx=(10, 5), sticky='w')

        self.carregar_cursos_disciplina()

        ctk.CTkLabel(self.frame, text= 'Valor da Disciplina', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=7, column=0, padx=10, pady=10, sticky='w')        
        self.entry_valor_mens = ctk.CTkEntry(self.frame, placeholder_text='')
        self.entry_valor_mens.grid(row=7, column= 1, padx=10, pady=10, sticky='w')
        self.entry_valor_mens.bind('<Return>', lambda event: self.validar_vlr_mens() and self.cadastrar_disc())
        self.erro_vlr_mens = ctk.CTkLabel(self.frame, text= '', text_color= 'red')
        self.erro_vlr_mens.grid(row=8, column= 1, padx=10, pady=5, sticky='w')

        
        self.label_sucesso = ctk.CTkLabel(self.frame, text='', text_color="green", font=("IMPACT", 28))
        self.label_sucesso.grid(row=9, column=0,columnspan= 2, pady=5, padx=20, sticky='ew')
        self.label_sucesso.configure(text= ' ')

        ctk.CTkButton(self.frame,
                      text='CONFIRMAR CADASTRO',
                      font=('IMPACT', 20),
                      text_color="#B5B2CA",
                      command=self.cadastrar_disc).grid(row=10, column=0, pady=10, padx=10, sticky='w')

        ctk.CTkButton(self.frame,
                      text='LIMPAR CAMPOS',
                      font=('IMPACT', 20),
                      text_color="#B5B2CA",
                      command=self.limpar_disc).grid(row=10, column=1, pady=10, padx=10, sticky='ew')
        
    def carregar_cursos_disciplina(self, manter_selecao=False):
        selecao_atual = self.combo_curso_disc.get().strip()

        cursos = listar_cursos_combo()

        if not cursos:
            self.combo_curso_disc.configure(
                values=["Nenhum curso cadastrado"],
                state="disabled"
            )
            self.combo_curso_disc.set("Nenhum curso cadastrado")
            return False

        valores_combo = [
            f"{id_curso} - {nome_curso}"
            for id_curso, nome_curso in cursos
        ]

        self.combo_curso_disc.configure(
            values=valores_combo,
            state="readonly"
        )

        if manter_selecao and selecao_atual in valores_combo:
            self.combo_curso_disc.set(selecao_atual)
        else:
            self.combo_curso_disc.set("Selecione um curso")

        return True
    
    def atualizar_combo_cursos_disciplina(self, event=None):
        self.carregar_cursos_disciplina(manter_selecao=True)

    def obter_id_curso_disciplina(self):
        texto = self.combo_curso_disc.get().strip()

        opcoes_invalidas = {
            "",
            "Selecione um curso",
            "Nenhum curso cadastrado",
            "Carregando cursos..."
        }

        if texto in opcoes_invalidas:
            return ""

        return texto.split(" - ", 1)[0].strip()

    def validar_curso_disciplina_combo(self):
        id_curso = self.obter_id_curso_disciplina()

        if not id_curso:
            self.erro_id_curso_disc.configure(text="Selecione um curso.")
            self.combo_curso_disc.focus_set()
            return False

        if not id_existe("curso", id_curso):
            self.erro_id_curso_disc.configure(text="Curso não encontrado.")
            self.combo_curso_disc.focus_set()
            return False

        self.erro_id_curso_disc.configure(text="")
        return True

    def cadastrar_disc(self):
        if not self.validar_disciplina():
            messagebox.showerror("Erro", "Preencha a disciplina corretamente.")
            return False

        if not self.validar_curso_disciplina_combo():
            messagebox.showerror("Erro", "Selecione um curso válido.")
            return False

        if not self.validar_vlr_mens():
            messagebox.showerror("Erro", "Informe corretamente o valor da disciplina.")
            return False

        dados = {
            "nome_disciplina": self.entry_disciplina.get().strip(),
            "ids_cursos": self.obter_id_curso_disciplina(),
            "valor_mensalidade": self.entry_valor_mens.get().strip()
        }

        try:
            novo_id = inserir_disciplina(dados)

            self.entry_num_disc.configure(state="normal")
            self.entry_num_disc.delete(0, END)
            self.entry_num_disc.insert(0, str(novo_id))
            self.entry_num_disc.configure(state="readonly")

            self.label_sucesso.configure(text="Cadastro realizado com sucesso!")

            self.winfo_toplevel().event_generate(
                "<<DisciplinaCadastrada>>",
                when="tail"
            )

            self.after(3000, self.esconder_sucesso)

            return True

        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
            return False

    def esconder_sucesso(self):
        self.label_sucesso.configure(text= ' ')
        self.limpar_disc()

    def limpar_disc(self):
        self.entry_disciplina.delete(0, END)

        self.entry_num_disc.configure(state="normal")
        self.entry_num_disc.delete(0, END)
        self.entry_num_disc.insert(0, " ")
        self.entry_num_disc.configure(state="readonly")

        self.combo_curso_disc.set("Selecione um curso")
        self.entry_valor_mens.delete(0, END)

        self.erro_NomeDisc.configure(text="")
        self.erro_id_curso_disc.configure(text="")
        self.erro_vlr_mens.configure(text="")
    
    def preencher_tree(self, dados):
        self.tree.delete(*self.tree.get_children())
        for linha in dados:
            self.tree.insert("", "end", values=linha)
