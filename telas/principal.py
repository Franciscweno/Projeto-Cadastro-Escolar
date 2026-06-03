import customtkinter as ctk
from validacoes import validacoes
from telas.aluno import JanelaAluno
from telas.professor import JanelaProfessor
from telas.disciplina import JanelaDisciplina
from telas.turma import JanelaTurma
from telas.curso import JanelaCurso
from telas.matricula import JanelaMatricula


class JanelaPrincipal(ctk.CTkFrame, validacoes):
    def __init__(self, parent, controller: 'App'):
        super().__init__(parent)
        self.controller = controller

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)

        self.FrameDireita = ctk.CTkFrame(self, corner_radius=200)
        self.FrameDireita.grid(row=0, column=1, rowspan=2, padx=(10, 30), sticky="nsew")
        self.FrameDireita.rowconfigure(0, weight=1)
        self.FrameDireita.columnconfigure(0, weight=1)

        self.menu_cadastro = {}

        self.FrameEsquerdaSuperior = ctk.CTkFrame(
            self, border_width=10, fg_color="#23222C", corner_radius=20
        )
        self.FrameEsquerdaSuperior.grid(row=0, column=0, padx=20, pady=20)

        self.FrameEsquerdaSuperior.grid_rowconfigure(0, weight=0)
        self.FrameEsquerdaSuperior.grid_columnconfigure(0, weight=0)

        self.FrameBotoes = ctk.CTkFrame(
            self, width=1000, height=600,
            border_width=10, fg_color="#23222C", corner_radius=1000
        )
        self.FrameBotoes.grid(row=1, column=0, pady=10, sticky='nsw', padx=50)

        self.FrameBotoes.columnconfigure(0, weight=2)
        for i in range(11):
            self.FrameBotoes.rowconfigure(i, weight=1)

        ctk.CTkLabel(
            self.FrameEsquerdaSuperior,
            text='M e n u P r i n c i p a l',
            text_color="#9692BB",
            font=('IMPACT', 48)
        ).grid(row=0, column=0)

        ctk.CTkButton(
            self.FrameBotoes,
            #height=80,
            text='CADASTRAR PROFESSOR',
            font=('IMPACT', 30),
            text_color="#B5B2CA",
            fg_color="#3E2EA7",
            hover_color="#26197A",
            command=lambda: self.menu_direita(JanelaProfessor)
        ).grid(row=0, column=0, sticky='ew', pady=15, padx=60)

        ctk.CTkButton(
            self.FrameBotoes,
            text='CADASTRAR ALUNO',
            #height=80,
            font=('IMPACT', 30),
            text_color="#B5B2CA",
            fg_color="#3E2EA7",
            hover_color="#26197A",
            command=lambda: self.menu_direita(JanelaAluno)
        ).grid(row=1, column=0, sticky='ew', pady=15, padx=60)

        ctk.CTkButton(
            self.FrameBotoes,
            text='MATRICULAR ALUNO',
            #height=80,
            font=('IMPACT', 30),
            text_color="#B5B2CA",
            fg_color="#3E2EA7",
            hover_color="#26197A",
            command=lambda: self.menu_direita(JanelaMatricula)
        ).grid(row=2, column=0, sticky='ew', pady=15, padx=60)

        ctk.CTkButton(
            self.FrameBotoes,
            #height=80,
            text='CADASTRAR DISCIPLINA',
            font=('IMPACT', 30),
            text_color="#B5B2CA",
            fg_color="#3E2EA7",
            hover_color="#26197A",
            command=lambda: self.menu_direita(JanelaDisciplina)
        ).grid(row=3, column=0, sticky='ew', pady=15, padx=60)

        ctk.CTkButton(
            self.FrameBotoes,
            #height=80,
            text='CADASTRAR TURMA',
            font=('IMPACT', 30),
            text_color="#B5B2CA",
            fg_color="#3E2EA7",
            hover_color="#26197A",
            command=lambda: self.menu_direita(JanelaTurma)
        ).grid(row=4, column=0, sticky='ew', pady=15, padx=60)

        ctk.CTkButton(self.FrameBotoes,
            #height=80,
            text='CADASTRAR CURSO',
            font=('IMPACT', 30),
            text_color="#B5B2CA",
            fg_color="#3E2EA7",
            hover_color="#26197A",
            command=lambda: self.menu_direita(JanelaCurso)
        ).grid(row=5, column=0, sticky='ew', pady=15, padx=60)

        ctk.CTkButton(
            self.FrameBotoes,
            #height=80,
            text='LOGOUT',
            font=('IMPACT', 30),
            text_color="#B5B2CA",
            fg_color="#3E2EA7",
            hover_color="#26197A",
            command=self.fazer_logout
        ).grid(row=6, column=0, sticky='ew', pady=15, padx=60)

    def fazer_logout(self):
        from telas.login import JanelaLogin
        self.controller.abrir_janela(JanelaLogin)

    def menu_direita(self, tela):
        for frame in self.menu_cadastro.values():
            frame.grid_forget()

        if tela not in self.menu_cadastro:
            frame_direita = tela(self.FrameDireita, self.controller)
            self.menu_cadastro[tela] = frame_direita

        frame = self.menu_cadastro[tela]
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

        if hasattr(frame, "tab"):
            frame.tab.set('CADASTRO')
