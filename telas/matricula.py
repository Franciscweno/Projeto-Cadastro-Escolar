import customtkinter as ctk
from tkinter import END, messagebox, ttk
from datetime import datetime as dt
from validacoes import validacoes
from banco import consultar_matriculas, id_existe, inserir_matricula, cancelar_matricula, calcular_total_turmas, buscar_aluno_por_id

class JanelaMatricula(ctk.CTkScrollableFrame, validacoes):
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

        self.aba_matricula()
        self.aba_consulta()

    def aba_consulta(self):
        self.frame = ctk.CTkFrame(self.tab_consulta, fg_color="transparent")
        self.frame.grid(row= 0, column= 0, padx=20, pady=20, sticky="nsew")
        self.tab_consulta.grid_rowconfigure(0, weight= 1)
        self.tab_consulta.grid_columnconfigure(0, weight= 1)
        self.frame.grid_rowconfigure(3, weight=1)

        self.frame.grid_columnconfigure(0, weight=0)
        self.frame.grid_columnconfigure(1, weight=0)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_columnconfigure(3, weight=0)
        self.grid_rowconfigure(0, weight= 1)
        self.grid_columnconfigure(0, weight = 1)

        ctk.CTkLabel(self.frame, text= 'CONSULTAR MATRICULA', font= ('IMPACT', 30), text_color= '#B5B2CA').grid(row= 0, column= 0, columnspan= 4, pady= 20)

        ctk.CTkLabel(self.frame, text="Buscar por:", font= ('IMPACT', 14)).grid(row=1, column=0, padx=10, pady=10)
        self.combo_filtro = ctk.CTkComboBox(self.frame, values=["ID Matrícula", "ID Aluno", "ID Turma(s)", "Nome", "CPF", "Curso", "Bolsista", "Status"], state='readonly', width=100)
        self.combo_filtro.set("ID Matrícula")
        self.combo_filtro.grid(row=1, column=1, padx=5,pady= 10, sticky= 'nsew')

        self.entry_busca = ctk.CTkEntry(self.frame, placeholder_text="", width=250)
        self.entry_busca.grid(row=1, column=2, padx=5, pady=10, sticky='nsew')

        self.label_dica_busca = ctk.CTkLabel(self.frame, text="Digite apenas números", text_color="#B5B2CA", font=("Arial", 10))
        self.label_dica_busca.grid(row=2, column=2, padx=5, sticky="w")
        self.configurar_validacao_consulta()

        self.btn_buscar = ctk.CTkButton(self.frame, text="🔍", width=40, command= self.consultar_matricula)
        self.btn_buscar.grid(row=1, column=3, padx=5, pady= 10, sticky= 'nsew')

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Treeview", background="#2b2b2b", foreground="#B5B2CA", fieldbackground="#2b2b2b", borderwidth=0)
        self.style.map("Treeview", background=[('selected', '#3498db')])

        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_rowconfigure(4, weight=0)

        self.tree = ttk.Treeview(
            self.frame,
            columns=("ID", "Nome", "CPF", "Curso", "Turmas", "Bolsista", "%Bolsa",'Valor sem desconto', "Mensalidade Final", "Status"),
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
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("CPF", text="CPF")
        self.tree.heading("Curso", text="Curso")
        self.tree.heading("Turmas", text="Turmas")
        self.tree.heading("Bolsista", text="Bolsista")
        self.tree.heading("%Bolsa", text="%Bolsa")
        self.tree.heading("Valor sem desconto", text="Valor sem desconto")
        self.tree.heading("Mensalidade Final", text="Mensalidade Final")
        self.tree.heading("Status", text="Status")

        self.tree.column("ID", width=40, stretch=False)
        self.tree.column("Nome", width=200, stretch=False)
        self.tree.column("CPF", width=110, stretch=False)
        self.tree.column("Curso", width=200, stretch=False)
        self.tree.column("Turmas", width=60, stretch=False)
        self.tree.column("Bolsista", width=70, stretch=False)
        self.tree.column("%Bolsa", width=70, stretch=False)
        self.tree.column("Valor sem desconto", width=130, stretch=False)
        self.tree.column("Mensalidade Final", width=130, stretch=False)
        self.tree.column("Status", width=90, stretch=False)

    def consultar_matricula(self):
        try:
            if not self.validar_termo_busca_consulta():
                return

            dados = consultar_matriculas(
                self.filtro_busca_consulta(),
                self.termo_busca_consulta()
            )

            self.tratar_resultado_consulta(dados, "matrícula")

        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    def bloquear_digitacao_ids_turmas(self, event=None):
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

        if event.char.isdigit() or event.char in [",", " "]:
            return None

        return "break"


    def atualizar_mensalidade_turmas(self, event=None):
        texto_turmas = self.entry_idturma_mat.get().strip()

        if not texto_turmas:
            self.preencher_mensalidade(0)
            self.erro_mensalidade.configure(text="")
            return

        try:
            total = calcular_total_turmas(texto_turmas)
            self.preencher_mensalidade(total)
            self.erro_mensalidade.configure(text="")

            if self.combo_bolsa.get().strip() == "Sim" and self.entry_bolsa.get().strip():
                self.aplicar_desconto()

        except ValueError as erro:
            self.preencher_mensalidade(0)
            self.erro_mensalidade.configure(text=str(erro))

    def aba_matricula(self):
        self.frame = ctk.CTkFrame(self.tab_cadastro)
        self.frame.grid(row= 0, column= 0, padx=20, pady=20, sticky="nsew")
        self.tab_cadastro.grid_rowconfigure(0, weight= 1)
        self.tab_cadastro.grid_columnconfigure(0, weight= 1)
        self.grid_rowconfigure(0, weight= 1)
        self.grid_columnconfigure(0, weight = 1)
        self.frame.grid_columnconfigure(0, weight=0, minsize=180)
        self.frame.grid_columnconfigure(1, weight=1, minsize=280)
        self.frame.grid_rowconfigure(18, minsize=60)

        #LABEL SUCESSO
        self.label_sucesso = ctk.CTkLabel(self.frame, text=' ', text_color="green", font=("IMPACT", 28))
        self.label_sucesso.grid(row=18, column=0,columnspan= 2, padx=10, pady=5, sticky='ew')
        self.label_sucesso.configure(text='')
        

        ctk.CTkLabel(self.frame, text= 'MATRÍCULA DO ALUNO', font= ('IMPACT', 30), text_color= '#B5B2CA').grid(row= 0, column= 0, columnspan= 2, pady= 20)

        ctk.CTkLabel(self.frame, text="ID_MATRICULA", font=('IMPACT', 14), text_color="#B5B2CA").grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        self.entry_mat = ctk.CTkEntry(self.frame, placeholder_text='', fg_color= "#6B6B6B")
        self.entry_mat.grid(row=1, column=1, padx=(10, 5), sticky='w')
        self.erro_entry_mat = ctk.CTkLabel(self.frame, text= '', text_color= 'red')
        self.erro_entry_mat.grid(row= 2, column= 0, padx= 15, sticky= 'w')
        self.entry_mat.insert(0, ' ')
        self.entry_mat.configure(state= 'readonly')

        ctk.CTkLabel(self.frame, text="ID_Turma(s)", font=('IMPACT', 14), text_color="#B5B2CA").grid(row=3, column=0, padx=10, pady=10, sticky='ew')
        self.entry_idturma_mat = ctk.CTkEntry(self.frame, placeholder_text='')        
        self.entry_idturma_mat.grid(row= 3, column= 1, padx=10, pady= 10, sticky= 'ew')
        self.entry_idturma_mat.bind("<KeyPress>", self.bloquear_digitacao_ids_turmas)
        self.entry_idturma_mat.bind("<KeyRelease>", self.atualizar_mensalidade_turmas)
        self.entry_idturma_mat.bind('<Return>', lambda event: self.validar_idturma_mat() and self.entry_id_alunomat.focus_set())
        self.label_erro_id_turmamat = ctk.CTkLabel(self.frame, text='', text_color='red')
        self.label_erro_id_turmamat.grid(row=4, column=1,padx= 15, sticky='ew')

        ctk.CTkLabel(self.frame, text="ID_Aluno", font=('IMPACT', 14), text_color="#B5B2CA").grid(row=5, column=0, padx=10, pady=10, sticky='ew')
        self.frame_aluno_matricula = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.frame_aluno_matricula.grid(row=5, column=1, padx=10, pady=10, sticky='ew')
        self.frame_aluno_matricula.grid_columnconfigure(0, weight=0)
        self.frame_aluno_matricula.grid_columnconfigure(1, weight=1)
        self.frame_aluno_matricula.grid_columnconfigure(2, weight=0)
        self.entry_id_alunomat = ctk.CTkEntry(self.frame_aluno_matricula,placeholder_text='ID',width=70)
        self.entry_id_alunomat.grid(row=0, column=0, padx=(0, 5), sticky='w')

        self.entry_nome_aluno = ctk.CTkEntry(
            self.frame_aluno_matricula,
            placeholder_text='Nome do aluno',
            fg_color="#6B6B6B"
        )
        self.entry_nome_aluno.grid(row=0, column=1, padx=(0, 5), sticky='ew')
        self.entry_nome_aluno.configure(state="readonly")

        self.btn_limpar_aluno = ctk.CTkButton(
            self.frame_aluno_matricula,
            text="X",
            width=32,
            fg_color="#E40101",
            hover_color="#9B0000",
            text_color="white",
            font=("Arial", 14, "bold"),
            command=self.limpar_aluno_matricula
        )
        self.btn_limpar_aluno.grid(row=0, column=2, sticky='e')

        self.entry_id_alunomat.bind("<KeyPress>", self.bloquear_digitacao_id_aluno_matricula)
        self.entry_id_alunomat.bind("<Return>", self.buscar_aluno_matricula)

        self.label_erro_alunomat = ctk.CTkLabel(
            self.frame,
            text='',
            text_color='red'
        )
        self.label_erro_alunomat.grid(row=6, column=1, padx=15, sticky='w')
        
        ctk.CTkLabel(self.frame, text= 'Data da Matrícula', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=7, column=0, padx=10, pady=10, sticky='ew')
        self.entry_datamat = ctk.CTkEntry(self.frame, placeholder_text='')
        self.entry_datamat.grid(row= 7, column=1, padx=10, pady=10, sticky='ew')
        self.entry_datamat.bind('<Return>', lambda event: self.validar_data_mat() and self.entry_mensalidade.focus_set())
        self.entry_datamat.bind('<KeyRelease>', lambda event: self.formatar_data_digitando(self.entry_datamat))
        self.entry_datamat.bind('<FocusOut>', lambda event: self.completar_ano_data(self.entry_datamat))
        self.label_erro_datamat = ctk.CTkLabel(self.frame, text= '',text_color= 'red')
        self.label_erro_datamat.grid(row= 8, column= 1, padx=10, pady=5, sticky='ew')

        ctk.CTkLabel(self.frame, text= 'Bolsista', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=11, column=0, padx=10, pady=10, sticky='ew')
        self.combo_bolsa = ctk.CTkComboBox(self.frame, 
                                                values= ['Selecione', 
                                                         'Sim', 
                                                         'Não'], 
                                                         state= 'readonly',
                                                         command=lambda opcao: self.bolsa(opcao))
        self.combo_bolsa.grid(row= 11, column=1, padx=10, pady=10, sticky='ew')
        self.combo_bolsa.set('Selecione')
        self.erro_combo_bolsa = ctk.CTkLabel(self.frame, text= '', text_color= 'red')
        self.erro_combo_bolsa.grid(row= 12, column= 1, padx=10, pady=5, sticky='eew')


        ctk.CTkLabel(self.frame, text= 'Mensalidade sem desconto', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=9, column=0, padx=10, pady=10, sticky='ew')        
        self.entry_mensalidade = ctk.CTkEntry(self.frame, placeholder_text='', state= 'readonly')
        self.entry_mensalidade.grid(row=9, column= 1, padx=10, pady=10, sticky='eew')
        self.erro_mensalidade = ctk.CTkLabel(self.frame, text= '', text_color= 'red')
        self.erro_mensalidade.grid(row= 10, column=1, padx=10, pady=5, sticky='eew')

        #***************************************************************************************************************************************************

        ctk.CTkLabel(self.frame, text= '% Bolsa', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=13, column=0, padx=10, pady=10, sticky='ew')        
        self.entry_bolsa = ctk.CTkEntry(self.frame, placeholder_text='', state= 'disabled', fg_color= "#6B6B6B")
        self.entry_bolsa.grid(row=13, column= 1, padx=10, pady=10, sticky='ew')
        self.entry_bolsa.bind('<Return>', self.aplicar_desconto)
        self.erro_bolsa = ctk.CTkLabel(self.frame, text= '', text_color= 'red')
        self.erro_bolsa.grid(row= 14, column= 1, padx=10, pady=5, sticky='ew')

        ctk.CTkLabel(self.frame, text= 'valor com desconto', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=15, column=0, padx=10, pady=10, sticky='ew')
        self.entry_novo_valor = ctk.CTkEntry(self.frame, placeholder_text='', state= 'disabled',fg_color= "#6B6B6B")
        self.entry_novo_valor.grid(row=15, column= 1, padx= 10, pady=10, sticky='ew')


        ctk.CTkButton(self.frame,
                      text='CONFIRMAR MATRICULA',
                      font=('IMPACT', 20),
                      text_color="#B5B2CA",
                      command= self.cadastrar).grid(row=19, column=0, padx=5, pady=10, sticky='ew')

        ctk.CTkButton(self.frame,
                      text='LIMPAR CAMPOS',
                      font=('IMPACT', 20),
                      text_color="#B5B2CA",
                      command=self.limpar_campos).grid(row=19, column=1, padx=5, pady=10, sticky='ew')
        
        ctk.CTkButton(self.frame,
                      text='CANCELAR MATRICULA',
                      font=('IMPACT', 20),
                      fg_color="#E40101",
                      hover_color= "#9B0000",
                      text_color= "#B5B2CA",
                      command= self.cancelar_matricula_tela).grid(row=20, column=0, columnspan= 2, padx=5, pady=10, sticky='ew')

    def bloquear_digitacao_id_aluno_matricula(self, event=None):
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

    def preencher_nome_aluno_matricula(self, nome_aluno):
        self.entry_nome_aluno.configure(state="normal")
        self.entry_nome_aluno.delete(0, END)
        self.entry_nome_aluno.insert(0, nome_aluno)
        self.entry_nome_aluno.configure(state="readonly")

        self.entry_id_alunomat.configure(state="readonly")

    def limpar_aluno_matricula(self):
        self.entry_id_alunomat.configure(state="normal")
        self.entry_id_alunomat.delete(0, END)

        self.entry_nome_aluno.configure(state="normal")
        self.entry_nome_aluno.delete(0, END)
        self.entry_nome_aluno.configure(state="readonly")

        self.label_erro_alunomat.configure(text="")
        self.entry_id_alunomat.focus_set()

    def buscar_aluno_matricula(self, event=None):
        id_aluno = self.entry_id_alunomat.get().strip()

        if not id_aluno:
            self.label_erro_alunomat.configure(text="Informe o ID do aluno.")
            self.entry_id_alunomat.focus_set()
            return False

        if not id_aluno.isdigit():
            self.label_erro_alunomat.configure(text="Digite apenas números.")
            self.entry_id_alunomat.focus_set()
            return False

        try:
            nome_aluno = buscar_aluno_por_id(id_aluno)

            if nome_aluno is None:
                self.label_erro_alunomat.configure(text="Aluno não encontrado.")
                self.entry_id_alunomat.focus_set()
                return False

            self.preencher_nome_aluno_matricula(nome_aluno)
            self.label_erro_alunomat.configure(text="")
            self.entry_datamat.focus_set()

            return True

        except ValueError as erro:
            self.label_erro_alunomat.configure(text=str(erro))
            self.entry_id_alunomat.focus_set()
            return False

    def cadastrar(self):
        if not self.main_validacoes_matricula():
            messagebox.showerror("Erro", "Preencha os campos corretamente.")
            return False
        
        if not self.entry_nome_aluno.get().strip():
            if not self.buscar_aluno_matricula():
                messagebox.showerror("Erro", "Informe um aluno válido.")
                return False

        dados = {
            "ids_turmas": self.entry_idturma_mat.get().strip(),
            "id_aluno": self.entry_id_alunomat.get().strip(),
            "data_matricula": self.entry_datamat.get().strip(),
            "bolsista": self.combo_bolsa.get().strip(),
            "perc_bolsa": self.entry_bolsa.get().strip()
        }

        if dados["bolsista"] == "Não":
            dados["perc_bolsa"] = "0"

        try:
            if not id_existe("aluno", dados["id_aluno"]):
                raise ValueError("Aluno não encontrado.")

            id_matricula = inserir_matricula(dados)

            
            self.entry_mat.configure(state="normal")
            self.entry_mat.delete(0, END)
            self.entry_mat.insert(0, str(id_matricula))
            self.entry_mat.configure(state="readonly")

            self.mostrar_sucesso()

            return True

        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))
            return False
    
    def preencher_mensalidade(self, valor):
        self.entry_mensalidade.configure(state="normal")
        self.entry_mensalidade.delete(0, END)
        self.entry_mensalidade.insert(0, f"{valor:.2f}".replace(".", ","))
        self.entry_mensalidade.configure(state="disabled", fg_color="#6B6B6B")

    def centralizar_toplevel(self, janela, largura=420, altura=300, referencia=None):
            if referencia is None:
                referencia = self

            janela.update_idletasks()
            referencia.update_idletasks()

            ref_x = referencia.winfo_rootx()
            ref_y = referencia.winfo_rooty()
            ref_largura = referencia.winfo_width()
            ref_altura = referencia.winfo_height()

            x = ref_x + (ref_largura // 2) - (largura // 2)
            y = ref_y + (ref_altura // 2) - (altura // 2)

            janela.geometry(f"{largura}x{altura}+{x}+{y}")

    def cancelar_matricula_tela(self):
        janela = ctk.CTkToplevel(self)
        janela.title("Cancelar Matrícula")
        janela.geometry("420x300")
        janela.resizable(False, False)

        self.centralizar_toplevel(janela, largura=420, altura=300, referencia=self)

        janela.transient(self)
        janela.grab_set()
        janela.lift()
        janela.focus_force()

        janela.grid_columnconfigure(0, weight=1)
        janela.grid_columnconfigure(1, weight=1)

        def bloquear_id_matricula(event=None):
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

            # permite Ctrl+C, Ctrl+V, Ctrl+A, Ctrl+X
            if event.state & 0x4:
                return None

            if not event.char.isdigit():
                return "break"

            return None

        ctk.CTkLabel(
            janela,
            text="CANCELAR MATRÍCULA",
            font=("IMPACT", 24),
            text_color="#B5B2CA"
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 15), sticky="ew")

        ctk.CTkLabel(
            janela,
            text="ID da Matrícula",
            font=("IMPACT", 14),
            text_color="#B5B2CA"
        ).grid(row=1, column=0, padx=20, pady=10, sticky="w")

        entry_id = ctk.CTkEntry(janela, placeholder_text="Digite o ID")
        entry_id.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        erro_id = ctk.CTkLabel(janela, text="", text_color="red")
        erro_id.grid(row=2, column=1, padx=20, sticky="w")

        ctk.CTkLabel(
            janela,
            text="Data de Cancelamento",
            font=("IMPACT", 14),
            text_color="#B5B2CA"
        ).grid(row=3, column=0, padx=20, pady=10, sticky="w")

        entry_data = ctk.CTkEntry(janela, placeholder_text="DD/MM/AAAA")
        entry_data.grid(row=3, column=1, padx=20, pady=10, sticky="ew")

        erro_data = ctk.CTkLabel(janela, text="", text_color="red")
        erro_data.grid(row=4, column=1, padx=20, sticky="w")

        def formatar_data_cancelamento(event=None):
            numeros = ''.join(char for char in entry_data.get() if char.isdigit())
            numeros = numeros[:8]

            if len(numeros) <= 2:
                data_formatada = numeros
            elif len(numeros) <= 4:
                data_formatada = f"{numeros[:2]}/{numeros[2:]}"
            else:
                data_formatada = f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}"

            entry_data.delete(0, END)
            entry_data.insert(0, data_formatada)

        def completar_ano_cancelamento(event=None):
            numeros = ''.join(char for char in entry_data.get() if char.isdigit())

            if len(numeros) == 6:
                dia = numeros[:2]
                mes = numeros[2:4]
                ano = int(numeros[4:])

                if ano <= 29:
                    ano_completo = 2000 + ano
                else:
                    ano_completo = 1900 + ano

                data_formatada = f"{dia}/{mes}/{ano_completo}"

            elif len(numeros) == 8:
                data_formatada = f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}"

            else:
                data_formatada = entry_data.get().strip()

            entry_data.delete(0, END)
            entry_data.insert(0, data_formatada)

            return data_formatada

        def validar_data_cancelamento():
            data = completar_ano_cancelamento()

            if not data:
                erro_data.configure(text="Informe a data.")
                entry_data.focus_set()
                return False

            try:
                dt.strptime(data, "%d/%m/%Y")
            except ValueError:
                erro_data.configure(text="Data inválida.")
                entry_data.focus_set()
                return False

            erro_data.configure(text="")
            return True

        def executar_cancelamento():
            id_matricula = entry_id.get().strip()
            data_cancelamento = entry_data.get().strip()

            if not id_matricula:
                erro_id.configure(text="Informe o ID da matrícula.")
                entry_id.focus_set()
                return False

            if not id_matricula.isdigit():
                erro_id.configure(text="Digite apenas números.")
                entry_id.focus_set()
                return False

            erro_id.configure(text="")

            if not validar_data_cancelamento():
                return False

            confirmar = messagebox.askyesno(
                "Confirmar cancelamento",
                f"Deseja realmente cancelar a matrícula ID {id_matricula}?",
                default=messagebox.NO
            )

            if not confirmar:
                return False

            try:
                cancelar_matricula(id_matricula, data_cancelamento)

                messagebox.showinfo(
                    "Sucesso",
                    "Matrícula cancelada com sucesso."
                )

                janela.destroy()

                try:
                    self.consultar_matricula()
                except Exception:
                    pass

                return True

            except ValueError as erro:
                messagebox.showerror("Erro", str(erro))
                return False

        entry_id.bind("<KeyPress>", bloquear_id_matricula)

        entry_data.bind("<KeyRelease>", formatar_data_cancelamento)
        entry_data.bind("<FocusOut>", completar_ano_cancelamento)
        entry_id.bind("<Return>", lambda event: entry_data.focus_set())
        entry_data.bind("<Return>", lambda event: executar_cancelamento())

        ctk.CTkButton(
            janela,
            text="CANCELAR MATRÍCULA",
            font=("IMPACT", 18),
            fg_color="#E40101",
            hover_color="#9B0000",
            text_color="#B5B2CA",
            command=executar_cancelamento
        ).grid(row=5, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        ctk.CTkButton(
            janela,
            text="FECHAR",
            font=("IMPACT", 18),
            text_color="#B5B2CA",
            command=janela.destroy
        ).grid(row=6, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        entry_id.focus_set()
    
    def limpar_campos(self):     
        self.entry_mat.configure(state="normal")
        self.entry_mat.delete(0, END)
        self.entry_mat.configure(state="readonly")

        self.entry_bolsa.configure(state="normal")
        self.entry_bolsa.delete(0, END)
        self.entry_bolsa.configure(state="disabled", fg_color="#6B6B6B")

        self.entry_novo_valor.configure(state="normal")
        self.entry_novo_valor.delete(0, END)
        self.entry_novo_valor.configure(state="disabled", fg_color="#6B6B6B")

        self.combo_bolsa.set('Selecione')
        self.limpar_mensalidade()
        self.entry_mat.delete(0, END)
        self.entry_datamat.delete(0, END)
        self.limpar_aluno_matricula()
        self.entry_idturma_mat.delete(0, END)       

    def mostrar_sucesso(self):
        self.label_sucesso.configure(text="Cadastro realizado com sucesso!")
        self.after(3000, self.esconder_sucesso)
            
    def esconder_sucesso(self):
        self.label_sucesso.configure(text= ' ')
        self.limpar_campos()

    def preencher_tree(self, dados):
        self.tree.delete(*self.tree.get_children())
        for linha in dados:
            self.tree.insert("", "end", values=linha)

    def limpar_mensalidade(self):
        self.entry_mensalidade.configure(state="normal")
        self.entry_mensalidade.delete(0, END)
        self.entry_mensalidade.configure(state="disabled", fg_color="#6B6B6B")
