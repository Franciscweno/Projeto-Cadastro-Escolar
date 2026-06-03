import customtkinter as ctk


class JanelaLogin(ctk.CTkFrame):
    def __init__(self, parent, controller: 'App'):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frame_central = ctk.CTkFrame(self, width=300, height=270)
        self.frame_central.grid(row=0, column=0)
        self.frame_central.grid_propagate(False)

        for i in range(7):
            self.frame_central.grid_rowconfigure(i, weight=1)

        self.frame_central.grid_columnconfigure(0, weight=1)
        self.frame_central.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.frame_central,
            text='Instituição de Ensino',
            font=('IMPACT', 31),
            text_color="#5F5F5F"
        ).grid(row=0, column=0, columnspan=2, pady=(15, 10))

        ctk.CTkLabel(
            self.frame_central,
            text='Usuário',
            font=('Arial', 14)
        ).grid(row=1, column=0, columnspan=2, pady=(5, 0))

        self.entry_usuario = ctk.CTkEntry(
            self.frame_central,
            placeholder_text='USUARIO'
        )
        self.entry_usuario.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 10), sticky='ew')
        self.entry_usuario.bind('<Return>', lambda event: self.entry_senha.focus_set())

        ctk.CTkLabel(
            self.frame_central,
            text='Senha'
        ).grid(row=3, column=0, columnspan=2, pady=(5, 0))

        self.entry_senha = ctk.CTkEntry(
            self.frame_central,
            placeholder_text='*****',
            show='*'
        )
        self.entry_senha.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 10), sticky='ew')
        self.entry_senha.bind("<Return>", self.validar_usuario)

        self.erro_usuario = ctk.CTkLabel(
            self.frame_central,
            text='',
            text_color='red',
            font=('Arial', 10)
        )
        self.erro_usuario.grid(row=5, column=0, columnspan=2, pady=(0, 5))

        ctk.CTkButton(
            self.frame_central,
            text='Sair', font=('IMPACT', 16),
            text_color="#B5B2CA",
            fg_color="#3E2EA7",
            hover_color="#26197A",
            command=self.controller.destroy
        ).grid(row=6, column=0, padx=(10, 5), pady=(10, 15), sticky='ew')

        ctk.CTkButton(
            self.frame_central,
            text='Login', font=('IMPACT', 16),
            text_color="#B5B2CA",
            fg_color="#3E2EA7",
            hover_color="#26197A",
            command=self.validar_usuario
        ).grid(row=6, column=1, padx=(5, 10), pady=(10, 15), sticky='ew')

    def validar_usuario(self, event=None):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()

        if not usuario:
            self.erro_usuario.configure(text='Preencha todos os campos')
            self.entry_usuario.focus_set()
            return False

        if not senha:
            self.erro_usuario.configure(text='Usuário e/ou Senha inválidos')
            self.entry_senha.focus_set()
            return False

        if usuario != '1' or senha != '1':
            self.erro_usuario.configure(text='Usuário e/ou Senha inválidos')
            self.entry_usuario.focus_set()
            return False

        from telas.principal import JanelaPrincipal
        self.erro_usuario.configure(text='')
        self.controller.abrir_janela(JanelaPrincipal)
        return True
