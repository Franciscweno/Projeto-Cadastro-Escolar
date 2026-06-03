import customtkinter as ctk
from telas.login import JanelaLogin
from telas.principal import JanelaPrincipal
from banco import criar_tabelas
import sys
import os

def caminho_recurso(caminho_relativo):
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base, caminho_relativo)

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title('Cadastro (IE)')

        try:
            self.iconbitmap("assets/icone.ico")
        except Exception:
            pass

        largura, altura = 1280 , 720
        x = (self.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")
        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (JanelaLogin, JanelaPrincipal):
            frame = F(self, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.abrir_janela(JanelaLogin)

    def abrir_janela(self, tela):
        frame = self.frames[tela]
        frame.tkraise()


if __name__ == "__main__":
    criar_tabelas()
    app = App()
    app.mainloop()
