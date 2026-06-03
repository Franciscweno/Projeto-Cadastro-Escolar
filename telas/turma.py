import customtkinter as ctk
from tkinter import END, ttk, messagebox
from validacoes import validacoes
from banco import consultar_turmas, id_existe, inserir_turma, buscar_disciplinas_por_curso, disciplina_pertence_ao_curso, buscar_professor_por_id, buscar_valor_curso_disciplina



class JanelaTurma(ctk.CTkScrollableFrame, validacoes):
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

        self.aba_turma()
        self.aba_consulta()
        self.winfo_toplevel().bind(
            "<<DisciplinaCadastrada>>",
            self.atualizar_combo_disciplinas_turma,
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

        ctk.CTkLabel(self.frame, text= 'CONSULTAR TURMA', font= ('IMPACT', 30), text_color= '#B5B2CA').grid(row= 0, column= 0, columnspan= 4, pady= 20)

        ctk.CTkLabel(self.frame, text="Buscar por:", font= ('IMPACT', 14)).grid(row=1, column=0, padx=10, pady=10)
        self.combo_filtro = ctk.CTkComboBox(self.frame, values=['ID Turma', "Curso", 'Disciplina', 'Professor', 'Dia da Semana', 'Turno'],state='readonly', width=100)
        self.combo_filtro.set("ID Turma")
        self.combo_filtro.grid(row=1, column=1, padx=5,pady= 10, sticky= 'nsew')

        self.entry_busca = ctk.CTkEntry(self.frame, placeholder_text="", width=250)
        self.entry_busca.grid(row=1, column=2, padx=5, pady=10, sticky='nsew')

        self.label_dica_busca = ctk.CTkLabel(self.frame, text="Digite apenas números", text_color="#B5B2CA", font=("Arial", 10))
        self.label_dica_busca.grid(row=2, column=2, padx=5, sticky="w")
        self.configurar_validacao_consulta()

        self.btn_buscar = ctk.CTkButton(self.frame, text="🔍", width=40, command=self.consultar_turma)
        self.btn_buscar.grid(row=1, column=3, padx=5, pady= 10, sticky= 'nsew')

        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", borderwidth=0)
        self.style.map("Treeview", background=[('selected', '#3498db')])

        self.tree = ttk.Treeview(
        self.frame,
        columns=("ID", "Disciplina", "Curso", "Professor", "Dia", "Turno", "Vagas", "Alunos ativos"),
        show="headings"
        )
        self.tree.grid(
            row=3,
            column=0,
            columnspan=4,
            padx=10,
            pady=(20, 0),
            sticky="nsew"
        )

        scroll_x = ttk.Scrollbar(
            self.frame,
            orient="horizontal",
            command=self.tree.xview
        )

        scroll_x.grid(
            row=4,
            column=0,
            columnspan=4,
            padx=10,
            pady=(0, 10),
            sticky="ew"
        )

        self.tree.configure(xscrollcommand=scroll_x.set)

        self.tree.heading("ID", text="ID")
        self.tree.heading("Disciplina", text="Disciplina")
        self.tree.heading("Curso", text="Curso")
        self.tree.heading("Professor", text="Professor")
        self.tree.heading("Dia", text="Dia")
        self.tree.heading("Turno", text="Turno")
        self.tree.heading("Vagas", text="Vagas")
        self.tree.heading("Alunos ativos", text="Alunos ativos")

        self.tree.column("ID", width=50)
        self.tree.column("Disciplina", width=130)
        self.tree.column("Curso", width=130)
        self.tree.column("Professor", width=130)
        self.tree.column("Dia", width=80)
        self.tree.column("Turno", width=80)
        self.tree.column("Vagas", width=60)
        self.tree.column("Alunos ativos", width=90)

    def consultar_turma(self):
        try:
            if not self.validar_termo_busca_consulta():
                return

            dados = consultar_turmas(
                self.filtro_busca_consulta(),
                self.termo_busca_consulta()
            )

            self.tratar_resultado_consulta(dados, "turma")

        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))



    def aba_turma(self):
        self.frame = ctk.CTkFrame(self.tab_cadastro)
        self.frame.grid(row= 0, column= 0, padx=20, pady=20, sticky="nsew")
        self.frame.grid_rowconfigure(5, minsize=22)
        self.tab_cadastro.grid_rowconfigure(0, weight= 0)
        self.tab_cadastro.grid_columnconfigure(0, weight= 1)
        self.grid_rowconfigure(0, weight= 1)
        self.grid_columnconfigure(0, weight = 1)
        self.frame.grid_columnconfigure(0, weight=0, minsize=180)
        self.frame.grid_columnconfigure(1, weight=1, minsize=280)
        self.frame.grid_rowconfigure(16, minsize=60)

        #LABEL SUCESSO
        self.label_sucesso = ctk.CTkLabel(self.frame, text=' ', text_color="green", font=("IMPACT", 28))
        self.label_sucesso.grid(row=16, column=0,columnspan= 2, padx=10, pady=5, sticky='ew')
        self.label_sucesso.configure(text='')
        

        ctk.CTkLabel(self.frame, text= 'CADASTRO DE TURMA', font= ('IMPACT', 30), text_color= '#B5B2CA').grid(row= 0, column= 0, columnspan= 2, pady= 20)

        ctk.CTkLabel(self.frame, text="ID_TURMA", font=('IMPACT', 14), text_color="#B5B2CA").grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        self.entry_turma = ctk.CTkEntry(self.frame, placeholder_text='', fg_color= "#6B6B6B")
        self.entry_turma.grid(row=1, column=1, padx=(10, 5), sticky='w')
        self.entry_turma.insert(0, ' ')
        self.entry_turma.configure(state= 'readonly')

        ctk.CTkLabel(self.frame, text="ID_CURSO", font=('IMPACT', 14), text_color="#B5B2CA").grid(row=2, column=0, padx=10, pady=10, sticky='ew')
        self.entry_id_curso = ctk.CTkEntry(self.frame, placeholder_text='')        
        self.entry_id_curso.grid(row= 2, column= 1, padx=10, pady= 10, sticky= 'ew')
        self.entry_id_curso.bind('<Return>',lambda event: self.carregar_disciplinas_do_curso(event, mostrar_erro=True) and self.combo_disciplina.focus_set())
        self.entry_id_curso.bind('<FocusOut>',lambda event: self.carregar_disciplinas_do_curso(event, mostrar_erro=False))
        self.entry_id_curso.bind('<KeyRelease>',self.resetar_combo_disciplinas)
        self.label_erro_id_curso = ctk.CTkLabel(self.frame, text='', text_color='red')
        self.label_erro_id_curso.grid(row=3, column=1,padx=10, pady=5, sticky='ew')

        ctk.CTkLabel(self.frame,text="ID_DISCIPLINA",font=('IMPACT', 14),text_color="#B5B2CA").grid(row=4, column=0, padx=10, pady=10, sticky='ew')
        self.combo_disciplina = ctk.CTkComboBox(self.frame,values=["Informe um curso válido"],state="disabled",command=lambda opcao: self.validar_disc_turma() and self.atualizar_valor_disciplina_turma() and self.entry_id_prof.focus_set())
        self.combo_disciplina.grid(row=4, column=1, padx=10, pady=10, sticky='ew')
        self.combo_disciplina.set("Informe um curso válido")
        self.label_erro_id_disc = ctk.CTkLabel(self.frame,text=' ',text_color='red', font= ('Arial', 10), height=18)
        self.label_erro_id_disc.grid(row=5, column=1, padx=10, pady=(0, 5), sticky='ew')
        
        ctk.CTkLabel(
            self.frame,
            text="ID_PROFESSOR",
            font=("IMPACT", 14),
            text_color="#B5B2CA"
        ).grid(row=6, column=0, padx=10, pady=10, sticky="ew")

        self.frame_professor_turma = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )
        self.frame_professor_turma.grid(row=6, column=1, padx=10, pady=10, sticky="ew")
        self.frame_professor_turma.grid_columnconfigure(1, weight=1)

        self.entry_id_prof = ctk.CTkEntry(
            self.frame_professor_turma,
            placeholder_text="ID",
            width=70
        )
        self.entry_id_prof.grid(row=0, column=0, padx=(0, 5), sticky="w")

        self.entry_nome_professor = ctk.CTkEntry(
            self.frame_professor_turma,
            placeholder_text="Nome do professor",
            fg_color="#6B6B6B"
        )
        self.entry_nome_professor.grid(row=0, column=1, padx=(0, 5), sticky="ew")
        self.entry_nome_professor.configure(state="readonly")

        self.btn_limpar_professor = ctk.CTkButton(
            self.frame_professor_turma,
            text="X",
            width=32,
            fg_color="#E40101",
            hover_color="#9B0000",
            text_color="white",
            font=("Arial", 14, "bold"),
            command=self.limpar_professor_turma
        )
        self.btn_limpar_professor.grid(row=0, column=2, sticky="w")

        self.entry_id_prof.bind(
            "<KeyPress>",
            self.bloquear_digitacao_id_professor_turma
        )

        self.entry_id_prof.bind(
            "<Return>",
            self.buscar_professor_turma
        )

        self.label_erro_id_prof = ctk.CTkLabel(
            self.frame,
            text=" ",
            text_color="red",
            height=18
        )
        self.label_erro_id_prof.grid(row=7, column=1, padx=10, pady=(0, 5), sticky="w")

        ctk.CTkLabel(self.frame, text= 'Dia da Semana', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=8, column=0, padx=10, pady=10, sticky='ew')
        self.combo_dia_semana = ctk.CTkComboBox(self.frame, 
                                                values= ['Selecione', 
                                                         'Segunda', 
                                                         'Terça', 
                                                         'Quarta', 
                                                         'Quinta', 
                                                         'Sexta', 
                                                         'Sábado', 
                                                         'Domingo'], 
                                                         state= 'readonly',
                                                         command= lambda value: self.validar_dia_semana() and self.combo_turno.focus_set())
        self.combo_dia_semana.grid(row= 8, column=1, padx=10, pady=10, sticky='ew')
        self.combo_dia_semana.set('Selecione')
        self.erro_dia_semana = ctk.CTkLabel(self.frame, text= '', text_color= 'red')
        self.erro_dia_semana.grid(row= 9, column= 1, padx=10, pady=5, sticky='ew')

                #******************************************************************************

        ctk.CTkLabel(self.frame, text= 'Turno', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=10, column=0, padx=10, pady=10, sticky='ew')
        self.combo_turno = ctk.CTkComboBox(self.frame, values= ['Selecione','Matutino', 'Vespertino', 'Noturno', 'Integral'],
                                           state= 'readonly',
                                           command= lambda value: self.validar_turno() and self.entry_qtd_vagas.focus_set())
        self.combo_turno.grid(row= 10, column=1, padx=10, pady=10, sticky='ew')
        self.combo_turno.set('Selecione')
        self.erro_turno = ctk.CTkLabel(self.frame, text= '', text_color= 'red')
        self.erro_turno.grid(row= 11, column=1, padx=10, pady=5, sticky='ew')

        ctk.CTkLabel(self.frame, text= 'Quantidade de vagas', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=12, column=0, padx=10, pady=10, sticky='ew')        
        self.entry_qtd_vagas = ctk.CTkEntry(self.frame, placeholder_text='')
        self.entry_qtd_vagas.grid(row=12, column= 1, padx=10, pady=10, sticky='ew')
        self.entry_qtd_vagas.bind('<Return>', lambda event: self.validar_qtd_vagas() and self.entry_valor_mens.focus_set())
        self.erro_vagas = ctk.CTkLabel(self.frame, text= '', text_color= 'red')
        self.erro_vagas.grid(row= 13, column=1, padx=10, pady=5, sticky='ew')

        ctk.CTkLabel(self.frame, text= 'Valor da Disciplina', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=14, column=0, padx=10, pady=10, sticky='ew')        
        self.entry_valor_mens = ctk.CTkEntry(self.frame, placeholder_text='', fg_color= '#6B6B6B')
        self.entry_valor_mens.grid(row=14, column= 1, padx=10, pady=10, sticky='ew')
        self.entry_valor_mens.configure(state= 'disabled')
        self.entry_valor_mens.bind('<Return>', lambda event: self.validar_vlr_mens() and self.validar_campos_turma())
        self.erro_vlr_mens = ctk.CTkLabel(self.frame, text= '', text_color= 'red')
        self.erro_vlr_mens.grid(row=15, column= 1, padx=10, pady=5, sticky='ew')

        ctk.CTkButton(self.frame,
                      text='CONFIRMAR CADASTRO',
                      font=('IMPACT', 20),
                      text_color="#B5B2CA",
                      command= self.cadastrar_turma).grid(row=17, column=0, padx=5, pady=10, sticky='ew')

        ctk.CTkButton(self.frame,
                      text='LIMPAR CAMPOS',
                      font=('IMPACT', 20),
                      text_color="#B5B2CA",
                      command=self.limpar_campos).grid(row=17, column=1, padx=5, pady=10, sticky='ew')


    def validar_disciplina_do_curso_turma(self):
        id_curso = self.entry_id_curso.get().strip()
        id_disciplina = self.obter_id_disciplina_selecionada()

        if not id_curso:
            self.label_erro_id_curso.configure(text="Informe o ID do curso.")
            self.entry_id_curso.focus_set()
            return False

        if not id_curso.isdigit():
            self.label_erro_id_curso.configure(text="Digite apenas números.")
            self.entry_id_curso.focus_set()
            return False

        if not id_disciplina:
            self.label_erro_id_disc.configure(text="Selecione uma disciplina.")
            self.combo_disciplina.focus_set()
            return False

        if not disciplina_pertence_ao_curso(id_curso, id_disciplina):
            self.label_erro_id_disc.configure(
                text="Disciplina não pertence ao curso informado."
            )
            self.combo_disciplina.focus_set()
            return False

        self.label_erro_id_disc.configure(text=" ")
        return True

    def resetar_combo_disciplinas(self, event=None):
        self.combo_disciplina.configure(
            values=["Informe um curso válido"],
            state="disabled"
        )
        self.combo_disciplina.set("Informe um curso válido")
        self.label_erro_id_disc.configure(text=" ")

    def atualizar_combo_disciplinas_turma(self, event=None):
        id_curso = self.entry_id_curso.get().strip()

        if not id_curso:
            return False

        if not id_curso.isdigit():
            return False

        if not id_existe("curso", id_curso):
            return False

        return self.carregar_disciplinas_do_curso(
            event=None,
            mostrar_erro=False,
            manter_selecao=True
        )

    def carregar_disciplinas_do_curso(self, event=None, mostrar_erro=False, manter_selecao=False):
        id_curso = self.entry_id_curso.get().strip()
        selecao_atual = self.combo_disciplina.get().strip()

        if not id_curso:
            self.resetar_combo_disciplinas()
            return False

        if not id_curso.isdigit():
            self.resetar_combo_disciplinas()
            self.label_erro_id_curso.configure(text="Digite apenas números")

            if mostrar_erro:
                messagebox.showerror("Erro", "Digite apenas números no ID do curso.")

            self.entry_id_curso.focus_set()
            return False

        if not id_existe("curso", id_curso):
            self.resetar_combo_disciplinas()
            self.label_erro_id_curso.configure(text="Curso não encontrado.")

            if mostrar_erro:
                messagebox.showerror("Erro", "Curso não encontrado.")

            self.entry_id_curso.focus_set()
            return False

        try:
            disciplinas = buscar_disciplinas_por_curso(id_curso)

            if not disciplinas:
                self.combo_disciplina.configure(
                    values=["Curso sem disciplinas"],
                    state="disabled"
                )
                self.combo_disciplina.set("Curso sem disciplinas")
                self.label_erro_id_disc.configure(text=" ")

                if mostrar_erro:
                    messagebox.showerror(
                        "Erro",
                        "Esse curso não possui disciplinas vinculadas."
                    )

                return False

            valores_combo = [
                f"{id_disciplina} - {nome_disciplina}"
                for id_disciplina, nome_disciplina in disciplinas
            ]

            self.combo_disciplina.configure(
                values=valores_combo,
                state="readonly"
            )

            if manter_selecao and selecao_atual in valores_combo:
                self.combo_disciplina.set(selecao_atual)
            else:
                self.combo_disciplina.set("Selecione")

            self.label_erro_id_curso.configure(text=" ")
            self.label_erro_id_disc.configure(text=" ")

            return True

        except ValueError as erro:
            self.resetar_combo_disciplinas()

            if mostrar_erro:
                messagebox.showerror("Erro", str(erro))

            return False

    def obter_id_disciplina_selecionada(self):
        texto = self.combo_disciplina.get().strip()

        opcoes_invalidas = {
            "",
            "Selecione",
            "Informe um curso válido",
            "Curso sem disciplinas"
        }

        if texto in opcoes_invalidas:
            return ""

        return texto.split(" - ", 1)[0].strip()

    def validar_disc_turma(self):
        id_curso = self.entry_id_curso.get().strip()
        id_disciplina = self.obter_id_disciplina_selecionada()

        if not id_curso:
            self.label_erro_id_disc.configure(text="Informe o curso primeiro.")
            self.entry_id_curso.focus_set()
            return False

        if not id_disciplina:
            self.label_erro_id_disc.configure(text="Selecione uma disciplina.")
            self.combo_disciplina.focus_set()
            return False

        if not disciplina_pertence_ao_curso(id_curso, id_disciplina):
            self.label_erro_id_disc.configure(
                text="Disciplina não pertence ao curso informado."
            )
            self.combo_disciplina.focus_set()
            return False

        self.label_erro_id_disc.configure(text="")
        return True

    def bloquear_digitacao_id_professor_turma(self, event=None):
        teclas_livres = {
            "BackSpace",
            "Delete",
            "Left",
            "Right",
            "Home",
            "End",
            "Tab",
            "Return",
            "Escape"
        }

        if event.keysym in teclas_livres:
            return None

        if event.state & 0x4:
            return None

        if not event.char.isdigit():
            return "break"

        return None

    def preencher_nome_professor_turma(self, nome_professor):
        self.entry_nome_professor.configure(state="normal")
        self.entry_nome_professor.delete(0, END)
        self.entry_nome_professor.insert(0, nome_professor)
        self.entry_nome_professor.configure(state="readonly")

        self.entry_id_prof.configure(state="readonly")

    def limpar_professor_turma(self):
        self.entry_id_prof.configure(state="normal")
        self.entry_id_prof.delete(0, END)

        self.entry_nome_professor.configure(state="normal")
        self.entry_nome_professor.delete(0, END)
        self.entry_nome_professor.configure(state="readonly")

        self.label_erro_id_prof.configure(text=" ")
        self.entry_id_prof.focus_set()

    def buscar_professor_turma(self, event=None):
        id_professor = self.entry_id_prof.get().strip()

        if not id_professor:
            self.label_erro_id_prof.configure(text="Informe o ID do professor.")
            self.entry_id_prof.focus_set()
            return False

        if not id_professor.isdigit():
            self.label_erro_id_prof.configure(text="Digite apenas números.")
            self.entry_id_prof.focus_set()
            return False

        try:
            nome_professor = buscar_professor_por_id(id_professor)

            if nome_professor is None:
                self.label_erro_id_prof.configure(text="Professor não encontrado.")
                self.entry_id_prof.focus_set()
                return False

            self.preencher_nome_professor_turma(nome_professor)
            self.label_erro_id_prof.configure(text=" ")
            self.combo_dia_semana.focus_set()

            return True

        except ValueError as erro:
            self.label_erro_id_prof.configure(text=str(erro))
            self.entry_id_prof.focus_set()
            return False

    def atualizar_valor_disciplina_turma(self, event=None):
        id_curso = self.entry_id_curso.get().strip()
        id_disciplina = self.obter_id_disciplina_selecionada()

        if not id_curso or not id_disciplina:
            self.limpar_valor_disciplina_turma()
            return False

        try:
            valor = buscar_valor_curso_disciplina(id_curso, id_disciplina)

            self.entry_valor_mens.configure(state="normal")
            self.entry_valor_mens.delete(0, END)
            self.entry_valor_mens.insert(0, f"{valor:.2f}".replace(".", ","))
            self.entry_valor_mens.configure(state="readonly")

            return True

        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
            self.limpar_valor_disciplina_turma()
            return False

    def limpar_valor_disciplina_turma(self):
        self.entry_valor_mens.configure(state="normal")
        self.entry_valor_mens.delete(0, END)
        self.entry_valor_mens.configure(state="disabled", fg_color="#6B6B6B")

    def cadastrar_turma(self):
        if not self.validar_campos_turma():
            messagebox.showerror("Erro", "Preencha os campos corretamente.")
            return False
        
        if not self.entry_nome_professor.get().strip():
            if not self.buscar_professor_turma():
                messagebox.showerror("Erro", "Informe um professor válido.")
                return False

        dados = {
        "id_curso": self.entry_id_curso.get().strip(),
        "id_disciplina": self.obter_id_disciplina_selecionada(),
        "id_professor": self.entry_id_prof.get().strip(),
        "dia_semana": self.combo_dia_semana.get().strip(),
        "turno": self.combo_turno.get().strip(),
        "qtd_vagas": self.entry_qtd_vagas.get().strip()
    }

        if not id_existe("curso", dados["id_curso"]):
            messagebox.showerror("Erro", "Curso não encontrado.")
            self.entry_id_curso.focus_set()
            return False
        
        if not dados["id_disciplina"]:
            messagebox.showerror("Erro", "Selecione uma disciplina.")
            self.combo_disciplina.focus_set()
            return False

        if not id_existe("disciplina", dados["id_disciplina"]):
            messagebox.showerror("Erro", "Disciplina não encontrada.")
            self.combo_disciplina.focus_set()
            return False
        
        if not disciplina_pertence_ao_curso(dados["id_curso"], dados["id_disciplina"]):
            messagebox.showerror(
                "Erro",
                "Essa disciplina não pertence ao curso informado."
            )
            self.combo_disciplina.focus_set()
            return False        

        if not id_existe("professor", dados["id_professor"]):
            messagebox.showerror("Erro", "Professor não encontrado.")
            self.entry_id_prof.focus_set()
            return False

        try:
            novo_id = inserir_turma(dados)

            self.entry_turma.configure(state="normal")
            self.entry_turma.delete(0, END)
            self.entry_turma.insert(0, str(novo_id))
            self.entry_turma.configure(state="readonly")

            self.label_sucesso.configure(text="Turma cadastrada com sucesso!")
            self.after(3000, self.esconder_sucesso)

            return True

        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
        return False

    def esconder_sucesso(self):
        self.label_sucesso.configure(text= ' ')
        self.limpar_campos()

    def limpar_campos(self):
        self.combo_dia_semana.set('Selecione')
        self.entry_id_curso.delete(0, END)
        self.resetar_combo_disciplinas()
        self.limpar_professor_turma()
        self.entry_qtd_vagas.delete(0, END)
        self.limpar_valor_disciplina_turma()
        self.combo_turno.set('Selecione')

    def preencher_tree(self, dados):
        self.tree.delete(*self.tree.get_children())
        for linha in dados:
            self.tree.insert("", "end", values=linha)


        