from datetime import datetime as dt
import requests
from tkinter import END
from tkinter import messagebox


class validacoes:
    def configurar_validacao_consulta(self):
        self.combo_filtro.configure(command=self.ao_mudar_filtro_consulta)

        # Bloqueia a tecla antes de ela entrar no campo
        self.entry_busca.bind("<KeyPress>", self.bloquear_digitacao_busca_consulta)

        # Usado principalmente para formatar CPF e limpar colagens
        self.entry_busca.bind("<KeyRelease>", self.formatar_digitacao_busca_consulta)

    def tratar_resultado_consulta(self, dados, nome_entidade):
        termo = self.termo_busca_consulta()

        # Limpa a tabela antes de mostrar novo resultado ou mensagem
        if hasattr(self, "tree"):
            self.tree.delete(*self.tree.get_children())

        if not dados:
            if termo:
                messagebox.showerror(
                    "Erro",
                    f"Nenhum cadastro de {nome_entidade} encontrado com os dados informados."
                )
            else:
                messagebox.showinfo(
                    "Consulta",
                    f"Nenhum cadastro de {nome_entidade} encontrado no sistema."
                )
            return False

        self.preencher_tree(dados)
        return True

    def ao_mudar_filtro_consulta(self, opcao=None):
        self.entry_busca.delete(0, END)

        dicas = {
            "ID": "Digite apenas números",
            "ID Matrícula": "Digite apenas números",
            "ID Aluno": "Digite apenas números",
            "ID Turma": "Digite apenas números",
            "ID Turma(s)": "Digite apenas números",
            "Turma": "Digite o ID da turma",
            "CPF": "Digite o CPF",
            "Nome": "Digite apenas letras",
            "Professor": "Digite apenas letras",
            "Aluno": "Digite apenas letras",
            "Curso": "Digite apenas letras",
            "Nome do curso": "Digite apenas letras",
            "Nome do Curso": "Digite apenas letras",
            "Disciplina": "Digite apenas letras",
            "Nome da Disciplina": "Digite apenas letras",
            "Status": "Digite Ativa ou Cancelada",
            "Bolsista": "Digite Sim ou Não",
            "Dia da Semana": "Digite o dia da semana",
            "Turno": "Digite o turno"
        }

        if hasattr(self, "label_dica_busca"):
            self.label_dica_busca.configure(
                text=dicas.get(opcao, "Digite sua busca")
            )

        self.frame.focus_set()

    def bloquear_digitacao_busca_consulta(self, event=None):
        filtro = self.combo_filtro.get()

        tecla = event.keysym
        char = event.char

        teclas_livres = {
            "BackSpace",
            "Delete",
            "Left",
            "Right",
            "Up",
            "Down",
            "Home",
            "End",
            "Tab",
            "Return",
            "Escape"
        }

        if tecla in teclas_livres:
            return None

        # Permite Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A
        if event.state & 0x4:
            return None

        if not char:
            return None

        filtros_id = {
            "ID",
            "ID Matrícula",
            "ID Aluno",
            "ID Turma",
            "ID Turma(s)",
            "Turma"
        }

        filtros_somente_letras = {
            "Nome",
            "Professor",
            "Aluno",
            "Bolsista",
            "Status",
            "Dia da Semana",
            "Turno",
            "Curso",
            "Nome do curso",
            "Nome do Curso",
            "Disciplina",
            "Nome da Disciplina"
        }

        if filtro in filtros_id:
            if not char.isdigit():
                return "break"

        elif filtro == "CPF":
            if not char.isdigit():
                return "break"

            numeros = ''.join(c for c in self.entry_busca.get() if c.isdigit())

            if len(numeros) >= 11:
                return "break"

        elif filtro in filtros_somente_letras:
            if not (char.isalpha() or char.isspace()):
                return "break"

        return None

    def formatar_digitacao_busca_consulta(self, event=None):
        filtro = self.combo_filtro.get()
        texto = self.entry_busca.get()

        filtros_id = {
            "ID",
            "ID Matrícula",
            "ID Aluno",
            "ID Turma",
            "ID Turma(s)",
            "Turma"
        }

        filtros_somente_letras = {
            "Nome",
            "Professor",
            "Aluno",
            "Bolsista",
            "Status",
            "Dia da Semana",
            "Turno",
            "Curso",
            "Nome do curso",
            "Nome do Curso",
            "Disciplina",
            "Nome da Disciplina"
        }

        if filtro in filtros_id:
            novo_texto = ''.join(char for char in texto if char.isdigit())

        elif filtro == "CPF":
            numeros = ''.join(char for char in texto if char.isdigit())
            numeros = numeros[:11]

            if len(numeros) <= 3:
                novo_texto = numeros
            elif len(numeros) <= 6:
                novo_texto = f"{numeros[:3]}.{numeros[3:]}"
            elif len(numeros) <= 9:
                novo_texto = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:]}"
            else:
                novo_texto = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"

        elif filtro in filtros_somente_letras:
            novo_texto = ''.join(
                char for char in texto
                if char.isalpha() or char.isspace()
            )

        else:
            novo_texto = texto

        if novo_texto != texto:
            self.entry_busca.delete(0, END)
            self.entry_busca.insert(0, novo_texto)

    def filtro_busca_consulta(self):
        filtro = self.combo_filtro.get()

        equivalencias = {
        "ID Turma(s)": "ID Turma"
    }

        return equivalencias.get(filtro, filtro)

    def termo_busca_consulta(self):
        filtro = self.combo_filtro.get()
        termo = self.entry_busca.get().strip()

        if filtro == "CPF":
            return ''.join(char for char in termo if char.isdigit())

        return termo

    def validar_termo_busca_consulta(self):
        filtro = self.combo_filtro.get()
        termo = self.entry_busca.get().strip()

        if not termo:
            return True

        filtros_id = {
            "ID",
            "ID Matrícula",
            "ID Aluno",
            "ID Turma",
            "ID Turma(s)",
            "Turma"
        }

        filtros_somente_letras = {
            "Nome",
            "Professor",
            "Aluno",
            "Bolsista",
            "Status",
            "Dia da Semana",
            "Turno",
            "Curso",
            "Nome do curso",
            "Nome do Curso",
            "Disciplina",
            "Nome da Disciplina"
        }

        if filtro in filtros_id:
            if not termo.isdigit():
                messagebox.showerror(
                    "Erro",
                    "Para buscar por ID, digite apenas números."
                )
                self.entry_busca.focus_set()
                return False

        elif filtro == "CPF":
            cpf = ''.join(char for char in termo if char.isdigit())

            if not cpf.isdigit() or len(cpf) != 11:
                messagebox.showerror(
                    "Erro",
                    "Para buscar por CPF, digite exatamente 11 números."
                )
                self.entry_busca.focus_set()
                return False

        elif filtro in filtros_somente_letras:
            if any(char.isdigit() for char in termo):
                messagebox.showerror(
                    "Erro",
                    "Para esse filtro, digite apenas letras."
                )
                self.entry_busca.focus_set()
                return False

            if not all(char.isalpha() or char.isspace() for char in termo):
                messagebox.showerror(
                    "Erro",
                    "Caracteres inválidos para esse filtro."
                )
                self.entry_busca.focus_set()
                return False

        return True

    def formatar_CPF_digitando(self, event=None):
        numeros = ''.join(char for char in self.entry_CPF.get() if char.isdigit())
        numeros = numeros[:11]

        if len(numeros) <= 3:
            cpf_formatado = numeros
        elif len(numeros) <= 6:
            cpf_formatado = f"{numeros[:3]}.{numeros[3:]}"
        elif len(numeros) <= 9:
            cpf_formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:]}"
        else:
            cpf_formatado = f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"

        self.entry_CPF.delete(0, END)
        self.entry_CPF.insert(0, cpf_formatado)

    def normalizar_email_digitando(self, event=None):
        email = self.entry_email.get().strip().lower()

        caracteres_permitidos = "abcdefghijklmnopqrstuvwxyz0123456789@._-+"

        email_limpo = ""
        qtd_arroba = 0

        for char in email:
            if char == "@":
                qtd_arroba += 1
                if qtd_arroba > 1:
                    continue

            if char in caracteres_permitidos:
                email_limpo += char

        self.entry_email.delete(0, END)
        self.entry_email.insert(0, email_limpo)

    def validar_nome(self):
        nome = self.entry_nome.get().strip()
        if not nome:
            self.nome_erro.configure(text='Campo Obrigatório')
            self.entry_nome.focus_set()
            return False

        if any(char.isdigit() for char in nome):
            self.nome_erro.configure(text='Caractere inválido')
            self.entry_nome.focus_set()
            return False

        if len(nome) < 10:
            self.nome_erro.configure(text='Nome muito pequeno')
            self.entry_nome.focus_set()
            return False
        self.nome_erro.configure(text='')
        return True

    def cpf_valido(self, cpf):
        cpf = ''.join(char for char in str(cpf) if char.isdigit())

        if len(cpf) != 11:
            return False

        if cpf == cpf[0] * 11:
            return False

        soma = 0
        for i in range(9):
            soma += int(cpf[i]) * (10 - i)

        primeiro_digito = (soma * 10) % 11

        if primeiro_digito == 10:
            primeiro_digito = 0

        if primeiro_digito != int(cpf[9]):
            return False

        soma = 0
        for i in range(10):
            soma += int(cpf[i]) * (11 - i)

        segundo_digito = (soma * 10) % 11

        if segundo_digito == 10:
            segundo_digito = 0

        if segundo_digito != int(cpf[10]):
            return False

        return True

    def validar_CPF(self):
        cpf = ''.join(char for char in self.entry_CPF.get() if char.isdigit())

        if not cpf:
            self.CPF_erro.configure(text='Campo obrigatório')
            self.entry_CPF.focus_set()
            return False

        if not self.cpf_valido(cpf):
            self.CPF_erro.configure(text='CPF inválido')
            self.entry_CPF.focus_set()
            return False

        cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

        self.entry_CPF.delete(0, END)
        self.entry_CPF.insert(0, cpf_formatado)

        self.CPF_erro.configure(text='')
        return True

    def validar_telefone(self):
        telefone = self.entry_telefone.get().strip().replace('-', '').replace('(', '').replace(')', '').replace('.', '').replace(' ', '')
        if not telefone:
            self.telefone_erro.configure(text='Campo obrigatório')
            self.entry_telefone.focus_set()
            return False
        if not telefone.isdigit():
            self.telefone_erro.configure(text='Digite apenas números')
            self.entry_telefone.focus_set()
            return False
        if len(telefone) < 10 or len(telefone) > 11:
            self.telefone_erro.configure(text='Telefone iválido')
            self.entry_telefone.focus_set()
            return False
        self.telefone_erro.configure(text='')
        return True

    def validar_Email(self):
        email = self.entry_email.get().strip().lower()

        if not email:
            self.email_erro.configure(text='Campo Obrigatório')
            self.entry_email.focus_set()
            return False

        caracteres_permitidos = "abcdefghijklmnopqrstuvwxyz0123456789@._-+"

        for char in email:
            if char not in caracteres_permitidos:
                self.email_erro.configure(text='Email inválido')
                self.entry_email.focus_set()
                return False

        if email.count("@") != 1:
            self.email_erro.configure(text='Digite um E-mail válido')
            self.entry_email.focus_set()
            return False

        usuario, dominio = email.split("@")

        if not usuario or not dominio:
            self.email_erro.configure(text='Digite um E-mail válido')
            self.entry_email.focus_set()
            return False

        if "." not in dominio:
            self.email_erro.configure(text='Digite um E-mail válido')
            self.entry_email.focus_set()
            return False

        if dominio.startswith(".") or dominio.endswith("."):
            self.email_erro.configure(text='Digite um E-mail válido')
            self.entry_email.focus_set()
            return False

        self.entry_email.delete(0, END)
        self.entry_email.insert(0, email)

        self.email_erro.configure(text='')
        return True

    def validar_Sexo(self):
        sexo = self.combo_sexo.get()
        if sexo == 'Selecione':
            self.sexo_erro.configure(text='Selecione uma opção de sexo')
            self.combo_sexo.focus_set()
            return False
        if sexo not in ['Masculino', 'Feminino', 'Outro']:
            self.sexo_erro.configure(text='Campo inválido')
            return False

        self.sexo_erro.configure(text='')
        return True

    def validar_disciplina(self):
        disciplina = self.entry_disciplina.get().strip()
        if not disciplina:
            self.erro_NomeDisc.configure(text='Campo Obrigatório')
            self.entry_disciplina.focus_set()
            return False
        if len(disciplina) < 5:
            self.erro_NomeDisc.configure(text='Nome Inválido')
            self.entry_disciplina.focus_set()
            return False
        if not disciplina.replace(' ', '').isalpha():
            self.erro_NomeDisc.configure(text='Caracteres não permitidos')
            self.entry_disciplina.focus_set()
            return False
        self.erro_NomeDisc.configure(text='')
        return True

    def validar_id_prof_turma(self):
        id_prof = self.entry_id_prof.get().strip()
        if not id_prof:
            self.label_erro_id_prof.configure(text= 'Campo Obrigatório')
            self.entry_id_prof.focus_set()
            return False
        
        if not id_prof.isdigit():
            self.label_erro_id_prof.configure(text= 'Digite Apenas números')
            self.entry_id_prof.focus_set()
            return False
        self.label_erro_id_prof.configure(text= '')
        return True

    def validar_CEP(self):
        cep = self.entry_CEP.get().strip().replace('-', '')
        if not cep:
            self.CEP_erro.configure(text='Campo Obrigatório')
            self.entry_CEP.focus_set()
            return False

        if not cep.isdigit():
            self.CEP_erro.configure(text='Digite apenas números')
            self.entry_CEP.focus_set()
            return False

        if len(cep) != 8:
            self.CEP_erro.configure(text='CEP deve conter 8 dígitos')
            self.entry_CEP.focus_set()
            return False

        self.CEP_erro.configure(text='')
        return True

    def validar_endereco(self):
        rua = self.entry_rua.get().strip()
        bairro = self.entry_bairro.get().strip()
        cidade = self.entry_cidade.get().strip()
        uf = self.combo_uf.get().strip()

        if not rua:
            self.CEP_erro.configure(text="Informe o logradouro.")
            self.entry_rua.focus_set()
            return False

        if not bairro:
            self.CEP_erro.configure(text="Informe o bairro.")
            self.entry_bairro.focus_set()
            return False

        if not cidade:
            self.CEP_erro.configure(text="Informe a cidade.")
            self.entry_cidade.focus_set()
            return False

        ufs_validas = {
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
            "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
            "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        }

        if uf not in ufs_validas:
            self.CEP_erro.configure(text="Selecione uma UF válida.")
            self.combo_uf.focus_set()
            return False

        self.CEP_erro.configure(text="")
        return True

    def buscar_CEP(self, event=None):
        if not self.validar_CEP():
            return

        cep = self.entry_CEP.get().strip().replace('-', '').replace('.', '')
        url = f"https://viacep.com.br/ws/{cep}/json/"

        try:
            resposta = requests.get(url, timeout=5)

            if resposta.status_code != 200:
                self.CEP_erro.configure(text='Erro ao consultar o CEP')
                return

            dados = resposta.json()

            if 'erro' in dados:
                self.CEP_erro.configure(text='CEP não encontrado')
                self.entry_CEP.focus_set()
                return

            self.entry_rua.delete(0, END)
            self.entry_bairro.delete(0, END)
            self.entry_cidade.delete(0, END)

            logradouro = dados.get("logradouro", "").strip()
            bairro = dados.get("bairro", "").strip()
            cidade = dados.get("localidade", "").strip()
            uf = dados.get("uf", "").strip()

            self.entry_rua.insert(0, logradouro)
            self.entry_bairro.insert(0, bairro)
            self.entry_cidade.insert(0, cidade)
            self.combo_uf.set(uf)

            if not logradouro or not bairro or not cidade or not uf:
                self.CEP_erro.configure(
                    text="CEP encontrado, mas complete o endereço manualmente."
                )
                self.entry_rua.focus_set()
                return

            self.CEP_erro.configure(text='')
            self.entry_telefone.focus_set()

        except requests.RequestException:
            self.CEP_erro.configure(text='Sem conexão com a API')
        return

    def main_validacoes(self):
        if not self.validar_nome():
            return False
        if not self.validar_CPF():
            return False
        if not self.validar_data_nasc():
            return False
        if not self.validar_telefone():
            return False
        if not self.validar_Email():
            return False
        if not self.validar_CEP():
            return False
        if not self.validar_endereco():
            return False
        if not self.validar_Sexo():
            return False
        return True

    def validacoes_dados_acad(self):
        if not self.validar_inst():
            return False
        if not self.validar_curso():
            return False
        if not self.validar_grau():
            return False
        if not self.validar_data_inicio():
            return False
        if not self.validar_data_fim():
            return False
        return True

    def validar_inst(self):
        inst = self.entry_inst.get().strip()
        if not inst:
            self.erro_inst.configure(text='Campo Obrigatório')
            self.entry_inst.focus_set()
            return False
        if inst.isdigit():
            self.erro_inst.configure(text='Insira uma instituição válida')
            self.entry_inst.focus_set()
            return False
        self.erro_inst.configure(text='')
        return True

    def validar_curso(self):
        curso = self.entry_curso.get().strip()
        if not curso:
            self.label_erro_curso.configure(text='Campo Obrigatório')
            self.entry_curso.focus_set()
            return False

        if len(curso) < 5:
            self.label_erro_curso.configure(text='Digite um curso válido')
            self.entry_curso.focus_set()
            return False
        
        if curso.isdigit():
            self.label_erro_curso.configure(text='Caractere Invalido')
            self.entry_curso.focus_set()
            return False
        self.label_erro_curso.configure(text='')
        return True
    
    def validar_id_curso(self):
        id = self.entry_id_curso.get().strip()
        if not id:
            self.label_erro_id_curso.configure(text= 'Campo Obrigatório')
            self.entry_id_curso.focus_set()
            return False
        if not id.isdigit():
            self.label_erro_id_curso.configure(text= 'Digite apenas números')
            self.entry_id_curso.focus_set()
            return False
        self.label_erro_id_curso.configure(text= '')
        return True

    def validar_carga_horaria(self):
        horas = self.entry_carga_horaria.get().strip()
        if not horas:
            self.erro_carga_horaria.configure(text= 'Campo Obrigatório')
            self.entry_carga_horaria.focus_set()
            return False
        if not horas.isdigit():
            self.erro_carga_horaria.configure(text= 'Digite apenas números')
            self.entry_carga_horaria.focus_set()
            return False
        if int(horas) < 30:
            self.erro_carga_horaria.configure(text= 'Quantidade de horas inválida')
            self.entry_carga_horaria.focus_set()
            return False
        self.erro_carga_horaria.configure(text= '')
        return True

    def validar_grau(self):
        grau = self.combo_grau.get()
        if grau == 'Grau':
            self.erro_grau.configure(text='Selecione um grau estudantil')
            return False
        if grau not in ['Graduação', 'Especialização', 'Mestrado', 'Doutorado', 'Pós-Doutorado']:
            self.erro_grau.configure(text='Campo inválido')
            return False
        self.erro_grau.configure(text='')
        return True
        
    def validar_dia_semana(self):
        dia = self.combo_dia_semana.get()
        if not dia or dia == 'Selecione':
            self.erro_dia_semana.configure(text= 'Selecione um dia da semana')
            return False
        if dia not in ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']:
            self.erro_dia_semana.configure(text= 'Campo invállido')
            return False
        self.erro_dia_semana.configure(text= '')
        return True
    
    def validar_turno(self):
        turno = self.combo_turno.get()
        if not turno or turno == 'Selecione':
            self.erro_turno.configure(text= 'Selecione um turno')
            return False
        if turno not in ['Selecione','Matutino', 'Vespertino', 'Noturno', 'Integral']:
            self.erro_turno.configure(text= 'Campo invállido')
            return False
        self.erro_turno.configure(text= '')
        return True
    
    def validar_qtd_vagas(self):
        vagas = self.entry_qtd_vagas.get().strip()
        if not vagas:
            self.erro_vagas.configure(text="Campo Obrigatório")
            self.entry_qtd_vagas.focus_set()
            return False
        if not vagas.isdigit():
            self.erro_vagas.configure(text="Digite apenas números")
            self.entry_qtd_vagas.focus_set()
            return False

        vagas = int(vagas)

        if vagas <= 0:
            self.erro_vagas.configure(text="Quantidade de vagas inválida")
            self.entry_qtd_vagas.focus_set()
            return False
        self.erro_vagas.configure(text="")
        return True
    
    def validar_qtd_mat(self):
        mat = self.entry_qtd_mat.get().strip()
        if not mat:
            self.erro_quant_mat.configure(text= 'Campo Obrigatório')
            self.entry_qtd_mat.focus_set()
            return False
        if not mat.isdigit():
            self.erro_quant_mat.configure(text= 'Digite apenas números')
            self.entry_qtd_mat.focus_set()
            return False
        if int(mat) < 30 or int(mat) > 40:
            self.erro_quant_mat.configure(text= 'Quantidade de matrículas inválida')
            self.entry_qtd_mat.focus_set()
            return False
        matriculas = int(mat)
        vagas = self.validar_qtd_vagas()

        if vagas is False:
            return False
        
        if matriculas > vagas:
            messagebox.showerror('Erro', 'Quantidade de matrículas não pode ser maior que a quantidade de vagas')
            self.entry_qtd_mat.focus_set()
            return False
        return True
           
    def validar_vlr_mens(self):
        valor = self.entry_valor_mens.get().strip().replace(".", "").replace(",", ".")
        if not valor:
            self.erro_vlr_mens.configure(text= 'Campo Obrigatório')
            self.entry_valor_mens.focus_set()
            return False
        
        try:
            valor = float(valor)
        except ValueError:
            self.erro_vlr_mens.configure(text="Valor inválido")
            self.entry_valor_mens.focus_set()
            return False

        if valor <= 0:
            self.erro_vlr_mens.configure(text="Valor inválido")
            self.entry_valor_mens.focus_set()
            return False

        self.erro_vlr_mens.configure(text="")
        return True

    def formatar_data_digitando(self, entry):
        numeros = ''.join(char for char in entry.get() if char.isdigit())
        numeros = numeros[:8]

        if len(numeros) <= 2:
            data_formatada = numeros
        elif len(numeros) <= 4:
            data_formatada = f'{numeros[:2]}/{numeros[2:]}'
        else:
            data_formatada = f'{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}'

        entry.delete(0, END)
        entry.insert(0, data_formatada)

    def completar_ano_data(self, entry):
        numeros = ''.join(char for char in entry.get() if char.isdigit())

        if len(numeros) == 6:
            dia = numeros[:2]
            mes = numeros[2:4]
            ano = int(numeros[4:])
            if ano <= 29:
                ano_completo = 2000 + ano
            else:
                ano_completo = 1900 + ano
            data_formatada = f'{dia}/{mes}/{ano_completo}'
        
        elif len(numeros) == 8:
            data_formatada = f'{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}'
        else:
            data_formatada = entry.get().strip()

        entry.delete(0, END)
        entry.insert(0, data_formatada)
        return data_formatada
    
    def validar_data_nasc(self):
        data = self.completar_ano_data(self.entry_data_nasc)
        if not data:
            self.erro_data_nasc.configure(text= 'Campo Obrigatório')
            return False
        try:
            dt.strptime(data, "%d/%m/%Y")
            self.erro_data_nasc.configure(text='')
            return True
        except ValueError:
            self.erro_data_nasc.configure(text='Data iválida')
            self.entry_data_nasc.focus_set()
            return False

    def validar_data_inicio(self):
        data_str = self.completar_ano_data(self.entry_data_inicio)

        if not data_str:
            self.erro_dt_inicio.configure(text='Campo Obrigatório')
            return False

        try:
            dt.strptime(data_str, "%d/%m/%Y")
            self.erro_dt_inicio.configure(text='')
            return True
        except ValueError:
            self.erro_dt_inicio.configure(text='Data inválida')
            self.entry_data_inicio.focus_set()
            return False

    def validar_data_fim(self):
        data_inicio_str = self.completar_ano_data(self.entry_data_inicio)
        data_fim_str = self.completar_ano_data(self.entry_data_fim)

        if not data_fim_str:
            self.erro_dt_fim.configure(text='Campo Obrigatório')
            return False

        try:
            data_inicio = dt.strptime(data_inicio_str, "%d/%m/%Y")
        except ValueError:
            self.erro_dt_inicio.configure(text='Data inicial inválida')
            self.entry_data_inicio.focus_set()
            return False

        try:
            data_fim = dt.strptime(data_fim_str, "%d/%m/%Y")
            self.erro_dt_fim.configure(text='')
        except ValueError:
            self.erro_dt_fim.configure(text='Data inválida')
            self.entry_data_fim.focus_set()
            return False

        if data_fim <= data_inicio:
            messagebox.showinfo('Erro', 'Data inicial não pode ser posterior à data final')
            self.entry_data_fim.focus_set()
            return False

        return True
    
    def validar_idturma_mat(self):
        texto = self.entry_idturma_mat.get().strip()

        if not texto:
            self.label_erro_id_turmamat.configure(text='Campo Obrigatório')
            self.entry_idturma_mat.focus_set()
            return False

        partes = texto.replace(";", ",").split(",")

        ids = []

        for parte in partes:
            parte = parte.strip()

            if not parte:
                continue

            if not parte.isdigit():
                self.label_erro_id_turmamat.configure(
                    text='Digite IDs separados por vírgula. Ex: 1,2,3'
                )
                self.entry_idturma_mat.focus_set()
                return False

            if parte in ids:
                self.label_erro_id_turmamat.configure(
                    text=f'Turma repetida: {parte}'
                )
                self.entry_idturma_mat.focus_set()
                return False

            ids.append(parte)

        if not ids:
            self.label_erro_id_turmamat.configure(text='Informe ao menos uma turma')
            self.entry_idturma_mat.focus_set()
            return False

        self.label_erro_id_turmamat.configure(text='')
        return True
    
    def validar_id_alunomat(self):
        id = self.entry_id_alunomat.get().strip()
        if not id:
            self.label_erro_alunomat.configure(text= 'Campo Obrigatório')
            self.entry_id_alunomat.focus_set()
            return False
        if not id.isdigit():
            self.label_erro_alunomat.configure(text= 'Digite apenas números')
            self.entry_id_alunomat.focus_set()
            return False
        self.label_erro_alunomat.configure(text= '')
        return True
    
    def validar_mensalidade(self):
        mens = self.entry_mensalidade.get().strip().replace(".", "").replace(",", ".")

        if not mens:
            self.erro_mensalidade.configure(text="Campo Obrigatório")
            self.entry_mensalidade.focus_set()
            return False

        try:
            mens = float(mens)
        except ValueError:
            self.erro_mensalidade.configure(text="Valor inválido")
            self.entry_mensalidade.focus_set()
            return False

        if mens <= 0:
            self.erro_mensalidade.configure(text="Valor inválido")
            self.entry_mensalidade.focus_set()
            return False

        self.erro_mensalidade.configure(text="")
        return True
    
    def calcular_bolsa(self):
        total_mens = self.entry_mensalidade.get().strip().replace(',', '.')
        porcentagem = self.entry_bolsa.get().strip().replace(',', '.')

        total_mens = float(total_mens)
        porcentagem = float(porcentagem)

        desconto = total_mens * porcentagem / 100
        valor_com_desc = total_mens - desconto

        return valor_com_desc
    
    def validar_entrada_porcbolsa(self):
        opcao = self.combo_bolsa.get().strip()
        if opcao == "Não":
            self.erro_bolsa.configure(text="")
            return True    
        if opcao == "Selecione":
            self.erro_bolsa.configure(text="")
            return True

        valor = self.entry_bolsa.get().strip().replace(',', '.')

        if not valor:
            self.erro_bolsa.configure(text="Campo obrigatório")
            self.entry_bolsa.focus_set()
            return False

        try:
            valor = float(valor)
        except ValueError:
            self.erro_bolsa.configure(text="Digite apenas números")
            self.entry_bolsa.focus_set()
            return False

        if valor <= 0 or valor > 100:
            self.erro_bolsa.configure(text="Porcentagem inválida")
            self.entry_bolsa.focus_set()
            return False

        self.erro_bolsa.configure(text="")
        return True
    
    def aplicar_desconto(self, event=None):
        if not self.validar_mensalidade():
            return False

        if not self.validar_entrada_porcbolsa():
            return False

        valor = self.calcular_bolsa()
        self.inserir_valor_novo(valor)
        

        return True
    
    def validar_data_mat(self):
        data_str = self.completar_ano_data(self.entry_datamat)

        if not data_str:
            self.label_erro_datamat.configure(text='Campo Obrigatório')
            return False

        try:
            dt.strptime(data_str, "%d/%m/%Y")
            self.label_erro_datamat.configure(text='')
            return True
        except ValueError:
            self.label_erro_datamat.configure(text='Data inválida')
            self.entry_datamat.focus_set()
            return False
        
    def validar_data_canc(self):
        data_str = self.entry_canc.get().strip()

        if not data_str:
            self.erro_canc.configure(text="")
            return True

        data_str = self.completar_ano_data(self.entry_canc)

        try:
            dt.strptime(data_str, "%d/%m/%Y")
            self.erro_canc.configure(text="")
            return True
        except ValueError:
            self.erro_canc.configure(text="Data inválida")
            self.entry_canc.focus_set()
            return False

    def validar_combo_bolsa(self):
        bolsa = self.combo_bolsa.get().strip()
        if bolsa == 'Selecione':
            self.erro_combo_bolsa.configure(text="Campo Obrigatório")
            return False
        self.erro_combo_bolsa.configure(text="")
        return True

    def inserir_valor_novo(self, valor):
        self.entry_novo_valor.configure(state="normal")
        self.entry_novo_valor.delete(0, END)
        self.entry_novo_valor.insert(0, f"{valor:.2f}".replace('.', ','))
        self.entry_novo_valor.configure(state="disabled")

    def validar_ids_cursos_disciplina(self):
        texto = self.entry_id_curso_disc.get().strip()

        if not texto:
            self.erro_id_curso_disc.configure(text="Informe o ID do curso.")
            self.entry_id_curso_disc.focus_set()
            return False

        partes = texto.replace(";", ",").split(",")

        ids = []

        for parte in partes:
            parte = parte.strip()

            if not parte:
                continue

            if not parte.isdigit():
                self.erro_id_curso_disc.configure(
                    text="Digite IDs separados por vírgula. Ex: 1,2,3"
                )
                self.entry_id_curso_disc.focus_set()
                return False

            if parte in ids:
                self.erro_id_curso_disc.configure(
                    text=f"Curso repetido: {parte}"
                )
                self.entry_id_curso_disc.focus_set()
                return False

            ids.append(parte)

        if not ids:
            self.erro_id_curso_disc.configure(text="Informe ao menos um curso.")
            self.entry_id_curso_disc.focus_set()
            return False

        self.erro_id_curso_disc.configure(text="")
        return True

    def bloquear_digitacao_ids_cursos_disciplina(self, event=None):
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

    def alternar_bolsa(self, opcao):
        if opcao == 'Selecione':
            self.entry_novo_valor.configure(state = 'disabled', fg_color= "#6B6B6B")
            self.entry_bolsa.configure(state="disabled", fg_color= "#6B6B6B")
            self.entry_bolsa.focus_set()
            self.erro_combo_bolsa.configure(text="")
        elif opcao == "Sim":
            self.entry_novo_valor.configure(state = 'normal', fg_color= '#343638')
            self.entry_bolsa.configure(state="normal", fg_color= '#343638')
            self.entry_bolsa.focus_set()
            self.erro_combo_bolsa.configure(text="")
        elif opcao == "Não":
            self.entry_novo_valor.configure(state = 'normal', fg_color= "#6B6B6B")
            self.entry_novo_valor.delete(0, END)
            self.entry_novo_valor.configure(state = 'disabled')

                                            
            self.entry_bolsa.configure(state="normal", fg_color= "#6B6B6B")
            self.entry_bolsa.delete(0, END)
            self.entry_bolsa.configure(state="disabled")
            self.erro_combo_bolsa.configure(text="")
        else:
            self.entry_bolsa.configure(state="normal", fg_color= '#343638')
            self.entry_bolsa.delete(0, END)
            self.entry_bolsa.configure(state="disabled")
            self.erro_combo_bolsa.configure(text="Selecione uma opção")
        
    def bolsa(self, opcao):
        self.alternar_bolsa(opcao)
        self.validar_combo_bolsa()

    def main_validacoes_matricula(self):
        if not self.validar_idturma_mat():
            return False
        if not self.validar_id_alunomat():
            return False
        if not self.validar_data_mat():
            return False
        if not self.validar_combo_bolsa():
            return False
        if self.combo_bolsa.get().strip() == "Sim":
            if not self.validar_entrada_porcbolsa():
                return False
            self.aplicar_desconto()

        return True
            
    def validar_campos_turma(self):
        if not self.validar_id_curso():
            return False
        if not self.validar_disc_turma():
            return False
        if not self.validar_id_prof_turma():
            return False
        if not self.validar_dia_semana():
            return False
        if not self.validar_turno():
            return False
        if not self.validar_qtd_vagas():
            return False
        return True
        