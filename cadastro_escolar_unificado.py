import customtkinter as ctk
import sqlite3
import os
import sys
import unicodedata
import requests
from datetime import datetime as dt
from tkinter import END, messagebox, ttk



# ============================================================
# BANCO DE DADOS E FUNÇÕES DE PERSISTÊNCIA
# ============================================================

if getattr(sys, "frozen", False):
    PASTA_PROJETO = os.path.dirname(sys.executable)
else:
    PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))

CAMINHO_BANCO = os.path.join(PASTA_PROJETO, "cadastro_escolar.db")


def conectar():
    con = sqlite3.connect(CAMINHO_BANCO)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def criar_tabelas():
    with conectar() as con:
        cursor = con.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aluno (
                id_aluno INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data_nasc TEXT NOT NULL,
                cpf TEXT NOT NULL UNIQUE,
                cep TEXT NOT NULL,
                rua TEXT NOT NULL,
                bairro TEXT NOT NULL,
                cidade TEXT NOT NULL,
                uf TEXT NOT NULL,
                telefone TEXT NOT NULL,
                email TEXT NOT NULL,
                sexo TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS professor (
                id_professor INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data_nasc TEXT NOT NULL,
                cpf TEXT NOT NULL UNIQUE,
                cep TEXT NOT NULL,
                rua TEXT NOT NULL,
                bairro TEXT NOT NULL,
                cidade TEXT NOT NULL,
                uf TEXT NOT NULL,
                telefone TEXT NOT NULL,
                email TEXT NOT NULL,
                sexo TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dados_acad_prof (
                id_dados_acad INTEGER PRIMARY KEY AUTOINCREMENT,
                id_professor INTEGER NOT NULL,
                instituicao TEXT NOT NULL,
                curso TEXT NOT NULL,
                grau TEXT NOT NULL,
                data_inicio TEXT NOT NULL,
                data_fim TEXT NOT NULL,

                FOREIGN KEY (id_professor)
                REFERENCES professor(id_professor)
                ON UPDATE CASCADE
                ON DELETE CASCADE
            )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS curso (
            id_curso INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_curso TEXT NOT NULL,
            nome_curso_norm TEXT NOT NULL UNIQUE,
            carga_horaria INTEGER NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS disciplina (
                id_disciplina INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_disciplina TEXT NOT NULL UNIQUE COLLATE NOCASE
            )
        """)

        cursor.execute("""
    CREATE TABLE IF NOT EXISTS curso_disciplina (
        id_curso_disciplina INTEGER PRIMARY KEY AUTOINCREMENT,
        id_curso INTEGER NOT NULL,
        id_disciplina INTEGER NOT NULL,
        valor_mensalidade REAL NOT NULL,

        FOREIGN KEY (id_curso)
        REFERENCES curso(id_curso)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

        FOREIGN KEY (id_disciplina)
        REFERENCES disciplina(id_disciplina)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

        UNIQUE (id_curso, id_disciplina)
    )
""")

        cursor.execute("""
    CREATE TABLE IF NOT EXISTS turma (
        id_turma INTEGER PRIMARY KEY AUTOINCREMENT,
        id_curso INTEGER NOT NULL,
        id_disciplina INTEGER NOT NULL,
        id_professor INTEGER NOT NULL,

        dia_semana TEXT NOT NULL
            CHECK (dia_semana IN (
                'Segunda',
                'Terça',
                'Quarta',
                'Quinta',
                'Sexta',
                'Sábado',
                'Domingo'
            )),

        turno TEXT NOT NULL
            CHECK (turno IN (
                'Matutino',
                'Vespertino',
                'Noturno',
                'Integral'
            )),

        qtd_vagas INTEGER NOT NULL
            CHECK (qtd_vagas > 0),

        FOREIGN KEY (id_curso)
        REFERENCES curso(id_curso)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

        FOREIGN KEY (id_disciplina)
        REFERENCES disciplina(id_disciplina)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

        FOREIGN KEY (id_professor)
        REFERENCES professor(id_professor)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
    )
""")

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_professor_dia_turno
                ON turma(id_professor, dia_semana, turno)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matricula (
                id_matricula INTEGER PRIMARY KEY AUTOINCREMENT,
                id_aluno INTEGER NOT NULL,

                data_matricula TEXT NOT NULL
                    CHECK (
                        data_matricula GLOB '[0-3][0-9]/[0-1][0-9]/[1-2][0-9][0-9][0-9]'
                    ),

                bolsista TEXT NOT NULL
                    CHECK (bolsista IN ('Sim', 'Não')),

                perc_bolsa REAL NOT NULL DEFAULT 0
                    CHECK (perc_bolsa >= 0 AND perc_bolsa <= 100),

                data_cancelamento TEXT
                    CHECK (
                        data_cancelamento IS NULL
                        OR data_cancelamento GLOB '[0-3][0-9]/[0-1][0-9]/[1-2][0-9][0-9][0-9]'
                    ),

                CHECK (
                    data_cancelamento IS NULL
                    OR (
                        substr(data_cancelamento, 7, 4) ||
                        substr(data_cancelamento, 4, 2) ||
                        substr(data_cancelamento, 1, 2)
                    ) >= (
                        substr(data_matricula, 7, 4) ||
                        substr(data_matricula, 4, 2) ||
                        substr(data_matricula, 1, 2)
                    )
                ),

                FOREIGN KEY (id_aluno)
                REFERENCES aluno(id_aluno)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matricula_turma (
                id_matricula_turma INTEGER PRIMARY KEY AUTOINCREMENT,
                id_matricula INTEGER NOT NULL,
                id_turma INTEGER NOT NULL,
                valor_mensalidade REAL NOT NULL,

                FOREIGN KEY (id_matricula)
                REFERENCES matricula(id_matricula)
                ON UPDATE CASCADE
                ON DELETE CASCADE,

                FOREIGN KEY (id_turma)
                REFERENCES turma(id_turma)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
    )
""")

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_aluno_matricula_ativa
                ON matricula(id_aluno)
                WHERE data_cancelamento IS NULL
""")

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_matricula_turma_unica
                ON matricula_turma(id_matricula, id_turma)
""")


        con.commit()

def cpf_valido(cpf):
    cpf = somente_numeros(cpf)

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

def somente_numeros(valor):
    return "".join(char for char in str(valor) if char.isdigit())

DIAS_SEMANA_VALIDOS = {
    "Segunda",
    "Terça",
    "Quarta",
    "Quinta",
    "Sexta",
    "Sábado",
    "Domingo"
}

TURNOS_VALIDOS = {
    "Matutino",
    "Vespertino",
    "Noturno",
    "Integral"
}


def validar_data_br_obrigatoria(data, nome_campo):
    data = str(data).strip()

    if not data:
        raise ValueError(f"{nome_campo} é obrigatória.")

    try:
        dt.strptime(data, "%d/%m/%Y")
    except ValueError:
        raise ValueError(f"{nome_campo} inválida. Use dd/mm/aaaa.")

    return data

def validar_dados_turma_banco(dados):
    dia_semana = str(dados["dia_semana"]).strip()
    turno = str(dados["turno"]).strip()
    qtd_vagas = str(dados["qtd_vagas"]).strip()

    if dia_semana not in DIAS_SEMANA_VALIDOS:
        raise ValueError("Dia da semana inválido.")

    if turno not in TURNOS_VALIDOS:
        raise ValueError("Turno inválido.")

    if not qtd_vagas.isdigit():
        raise ValueError("Quantidade de vagas deve conter apenas números.")

    if int(qtd_vagas) <= 0:
        raise ValueError("Quantidade de vagas deve ser maior que zero.")

    return True

def validar_dados_matricula_banco(data_matricula, bolsista, perc_bolsa):
    validar_data_br_obrigatoria(data_matricula, "Data de matrícula")

    if bolsista not in ["Sim", "Não"]:
        raise ValueError("Informe se o aluno é bolsista.")

    try:
        perc_bolsa = float(str(perc_bolsa).replace(",", "."))
    except ValueError:
        raise ValueError("Percentual de bolsa inválido.")

    if perc_bolsa < 0 or perc_bolsa > 100:
        raise ValueError("Percentual de bolsa deve estar entre 0 e 100.")

    if bolsista == "Sim" and perc_bolsa <= 0:
        raise ValueError("Aluno bolsista deve ter percentual de bolsa maior que zero.")

    if bolsista == "Não" and perc_bolsa != 0:
        raise ValueError("Aluno não bolsista deve ter percentual de bolsa igual a zero.")

    return perc_bolsa

def converter_data_br(data, nome_campo="Data"):
    data = str(data).strip()

    try:
        return dt.strptime(data, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError(f"{nome_campo} inválida.")

def dinheiro_para_float(valor):
    valor = str(valor).strip().replace("R$", "").replace(".", "").replace(",", ".")

    try:
        return float(valor)
    except ValueError:
        raise ValueError("Valor monetário inválido.")

def cpf_existe(tabela, cpf):
    cpf = somente_numeros(cpf)

    sql = f"SELECT 1 FROM {tabela} WHERE cpf = ? LIMIT 1"

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (cpf,))
        return cursor.fetchone() is not None

def normalizar_nome_pessoa(nome):
    nome = " ".join(str(nome).strip().split())

    nome_sem_acento = unicodedata.normalize("NFD", nome)
    nome_sem_acento = "".join(
        char for char in nome_sem_acento
        if unicodedata.category(char) != "Mn"
    )

    return nome_sem_acento.casefold()

def buscar_pessoa_por_cpf(tabela, cpf):
    if tabela not in ("aluno", "professor"):
        raise ValueError("Tabela inválida para busca de CPF.")

    cpf = somente_numeros(cpf)

    campos_id = {
        "aluno": "id_aluno",
        "professor": "id_professor"
    }

    campo_id = campos_id[tabela]

    sql = f"""
        SELECT {campo_id}, nome
        FROM {tabela}
        WHERE cpf = ?
        LIMIT 1
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (cpf,))
        return cursor.fetchone()

def validar_cpf_mesma_pessoa(cpf, nome, tipo_cadastro):
    cpf = somente_numeros(cpf)
    nome_normalizado = normalizar_nome_pessoa(nome)

    if not cpf_valido(cpf):
        raise ValueError("CPF inválido.")

    if tipo_cadastro == "aluno":
        tabela_atual = "aluno"
        tabela_outra = "professor"
        nome_tipo_atual = "aluno"
        nome_tipo_outra = "professor"

    elif tipo_cadastro == "professor":
        tabela_atual = "professor"
        tabela_outra = "aluno"
        nome_tipo_atual = "professor"
        nome_tipo_outra = "aluno"

    else:
        raise ValueError("Tipo de cadastro inválido.")

    pessoa_atual = buscar_pessoa_por_cpf(tabela_atual, cpf)

    if pessoa_atual is not None:
        raise ValueError(
            f"Já existe um {nome_tipo_atual} cadastrado com esse CPF."
        )

    pessoa_outra = buscar_pessoa_por_cpf(tabela_outra, cpf)

    if pessoa_outra is not None:
        nome_cadastrado = pessoa_outra[1]

        if normalizar_nome_pessoa(nome_cadastrado) != nome_normalizado:
            raise ValueError(
                f"Este CPF já está cadastrado para outra pessoa no cadastro de "
                f"{nome_tipo_outra}: {nome_cadastrado}."
            )

    return True

def normalizar_texto(valor):
    return " ".join(str(valor).strip().split())

def valor_existe_case_insensitive(tabela, coluna, valor):
    valor = normalizar_texto(valor)

    sql = f"""
        SELECT 1
        FROM {tabela}
        WHERE {coluna} = ? COLLATE NOCASE
        LIMIT 1
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (valor,))
        return cursor.fetchone() is not None

def valor_existe(tabela, coluna, valor):
    sql = f"SELECT 1 FROM {tabela} WHERE {coluna} = ? LIMIT 1"

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (valor.strip(),))
        return cursor.fetchone() is not None

def buscar_matricula_ativa_do_aluno(id_aluno):
    sql = """
        SELECT id_matricula
        FROM matricula
        WHERE id_aluno = ?
          AND data_cancelamento IS NULL
        LIMIT 1
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (int(id_aluno),))
        resultado = cursor.fetchone()

    if resultado:
        return resultado[0]

    return None

def matricula_ja_tem_turma(id_matricula, id_turma):
    sql = """
        SELECT 1
        FROM matricula_turma
        WHERE id_matricula = ?
          AND id_turma = ?
        LIMIT 1
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (int(id_matricula), int(id_turma)))
        return cursor.fetchone() is not None

def buscar_valor_disciplina_da_turma(id_turma):
    sql = """
        SELECT cd.valor_mensalidade
        FROM turma t
        JOIN curso_disciplina cd
            ON cd.id_curso = t.id_curso
           AND cd.id_disciplina = t.id_disciplina
        WHERE t.id_turma = ?
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (int(id_turma),))
        resultado = cursor.fetchone()

    if resultado is None:
        raise ValueError(
            "Valor da disciplina não encontrado para o curso dessa turma."
        )

    return float(resultado[0])

def contar_matriculas_ativas(id_turma):
    sql = """
        SELECT COUNT(DISTINCT mt.id_matricula)
        FROM matricula_turma mt
        JOIN matricula m
            ON m.id_matricula = mt.id_matricula
        WHERE mt.id_turma = ?
          AND m.data_cancelamento IS NULL
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (int(id_turma),))
        return cursor.fetchone()[0]

def turma_tem_vaga(id_turma):
    sql = """
        SELECT qtd_vagas
        FROM turma
        WHERE id_turma = ?
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (int(id_turma),))
        resultado = cursor.fetchone()

    if resultado is None:
        raise ValueError("Turma não encontrada.")

    qtd_vagas = resultado[0]
    matriculados = contar_matriculas_ativas(id_turma)

    return matriculados < qtd_vagas

def aluno_ja_matriculado_na_turma(id_aluno, id_turma):
    sql = """
        SELECT 1
        FROM matricula m
        JOIN matricula_turma mt
            ON mt.id_matricula = m.id_matricula
        WHERE m.id_aluno = ?
          AND mt.id_turma = ?
          AND m.data_cancelamento IS NULL
        LIMIT 1
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (int(id_aluno), int(id_turma)))
        return cursor.fetchone() is not None

def inserir_aluno(dados):
    cpf = somente_numeros(dados["cpf"])

    validar_cpf_mesma_pessoa(
        cpf=cpf,
        nome=dados["nome"],
        tipo_cadastro="aluno"
    )

    sql = """
        INSERT INTO aluno (
            nome,
            data_nasc,
            cpf,
            cep,
            rua,
            bairro,
            cidade,
            uf,
            telefone,
            email,
            sexo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    valores = (
        dados["nome"],
        dados["data_nasc"],
        cpf,
        somente_numeros(dados["cep"]),
        dados["rua"],
        dados["bairro"],
        dados["cidade"],
        dados["uf"],
        somente_numeros(dados["telefone"]),
        dados["email"],
        dados["sexo"]
    )

    try:
        with conectar() as con:
            cursor = con.cursor()
            cursor.execute(sql, valores)
            con.commit()
            return cursor.lastrowid
    except sqlite3.IntegrityError as erro:
        raise ValueError(f"Erro ao cadastrar aluno: {erro}")

def inserir_curso(dados):
    nome_curso = normalizar_texto(dados["nome_curso"])
    nome_curso_norm = normalizar_texto_comparacao(nome_curso)

    sql_verificar = """
        SELECT 1
        FROM curso
        WHERE nome_curso_norm = ?
        LIMIT 1
    """

    sql_inserir = """
        INSERT INTO curso (
            nome_curso,
            nome_curso_norm,
            carga_horaria
        )
        VALUES (?, ?, ?)
    """

    try:
        with conectar() as con:
            cursor = con.cursor()

            cursor.execute(sql_verificar, (nome_curso_norm,))
            if cursor.fetchone() is not None:
                raise ValueError("Já existe um curso cadastrado com esse nome.")

            cursor.execute(sql_inserir, (
                nome_curso,
                nome_curso_norm,
                int(dados["carga_horaria"])
            ))

            con.commit()
            return cursor.lastrowid

    except sqlite3.IntegrityError:
        raise ValueError("Já existe um curso cadastrado com esse nome.")

def extrair_ids_cursos(texto_ids):
    texto_ids = str(texto_ids).strip()

    if not texto_ids:
        raise ValueError("Informe ao menos um curso para a disciplina.")

    partes = texto_ids.replace(";", ",").split(",")

    ids_cursos = []
    repetidos = set()

    for parte in partes:
        parte = parte.strip()

        if not parte:
            continue

        if not parte.isdigit():
            raise ValueError("Digite os IDs dos cursos separados por vírgula. Exemplo: 1,2,3")

        id_curso = int(parte)

        if id_curso in ids_cursos:
            repetidos.add(id_curso)

        ids_cursos.append(id_curso)

    if repetidos:
        raise ValueError(f"Curso repetido no campo: {sorted(repetidos)}")

    if not ids_cursos:
        raise ValueError("Informe ao menos um curso para a disciplina.")

    return ids_cursos

def buscar_id_disciplina_por_nome(nome_disciplina):
    nome_disciplina = normalizar_texto(nome_disciplina)

    sql = """
        SELECT id_disciplina
        FROM disciplina
        WHERE nome_disciplina = ? COLLATE NOCASE
        LIMIT 1
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (nome_disciplina,))
        resultado = cursor.fetchone()

    if resultado:
        return resultado[0]

    return None

def curso_disciplina_existe(id_curso, id_disciplina):
    sql = """
        SELECT 1
        FROM curso_disciplina
        WHERE id_curso = ?
          AND id_disciplina = ?
        LIMIT 1
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (int(id_curso), int(id_disciplina)))
        return cursor.fetchone() is not None

def disciplina_pertence_ao_curso(id_curso, id_disciplina):
    return curso_disciplina_existe(id_curso, id_disciplina)

def buscar_disciplinas_por_curso(id_curso):
    validar_id_obrigatorio("curso", id_curso, "Curso")

    sql = """
        SELECT
            d.id_disciplina,
            d.nome_disciplina
        FROM curso_disciplina cd
        JOIN disciplina d
            ON d.id_disciplina = cd.id_disciplina
        WHERE cd.id_curso = ?
        ORDER BY d.nome_disciplina
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (int(id_curso),))
        return cursor.fetchall()

def inserir_disciplina(dados):
    nome_disciplina = normalizar_texto(dados["nome_disciplina"])
    ids_cursos = extrair_ids_cursos(dados["ids_cursos"])
    valor_mensalidade = dinheiro_para_float(dados["valor_mensalidade"])

    if valor_mensalidade <= 0:
        raise ValueError("Valor da disciplina inválido.")

    for id_curso in ids_cursos:
        validar_id_obrigatorio("curso", id_curso, f"Curso {id_curso}")

    try:
        with conectar() as con:
            cursor = con.cursor()

            cursor.execute("""
                SELECT id_disciplina
                FROM disciplina
                WHERE nome_disciplina = ? COLLATE NOCASE
                LIMIT 1
            """, (nome_disciplina,))

            resultado = cursor.fetchone()

            if resultado is None:
                cursor.execute("""
                    INSERT INTO disciplina (
                        nome_disciplina
                    )
                    VALUES (?)
                """, (nome_disciplina,))

                id_disciplina = cursor.lastrowid

            else:
                id_disciplina = resultado[0]

            cursos_ja_relacionados = []

            for id_curso in ids_cursos:
                cursor.execute("""
                    SELECT 1
                    FROM curso_disciplina
                    WHERE id_curso = ?
                      AND id_disciplina = ?
                    LIMIT 1
                """, (id_curso, id_disciplina))

                if cursor.fetchone() is not None:
                    cursos_ja_relacionados.append(id_curso)

            if cursos_ja_relacionados:
                raise ValueError(
                    f"Essa disciplina já está cadastrada no(s) curso(s): {cursos_ja_relacionados}"
                )

            for id_curso in ids_cursos:
                cursor.execute("""
                    INSERT INTO curso_disciplina (
                        id_curso,
                        id_disciplina,
                        valor_mensalidade
                    )
                    VALUES (?, ?, ?)
                """, (id_curso, id_disciplina, valor_mensalidade))

            con.commit()
            return id_disciplina

    except sqlite3.IntegrityError as erro:
        raise ValueError(f"Erro ao cadastrar disciplina: {erro}")

def professor_ocupado_no_horario(id_professor, dia_semana, turno):
    sql = """
        SELECT id_turma
        FROM turma
        WHERE id_professor = ?
          AND dia_semana = ?
          AND turno = ?
        LIMIT 1
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (
            int(id_professor),
            dia_semana,
            turno
        ))
        resultado = cursor.fetchone()

    if resultado:
        return resultado[0]

    return None

def inserir_turma(dados):
    validar_dados_turma_banco(dados)
    validar_id_obrigatorio("curso", dados["id_curso"], "Curso")
    validar_id_obrigatorio("disciplina", dados["id_disciplina"], "Disciplina")
    validar_id_obrigatorio("professor", dados["id_professor"], "Professor")

    if not disciplina_pertence_ao_curso(dados["id_curso"], dados["id_disciplina"]):
        raise ValueError(
        "A disciplina informada não pertence ao curso informado."
    )

    turma_existente = professor_ocupado_no_horario(
        dados["id_professor"],
        dados["dia_semana"],
        dados["turno"]
    )

    if turma_existente is not None:
        raise ValueError(
            f"Esse professor já está vinculado à turma ID {turma_existente} "
            f"nesse mesmo dia e turno."
        )

    sql = """
        INSERT INTO turma (
            id_curso,
            id_disciplina,
            id_professor,
            dia_semana,
            turno,
            qtd_vagas
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """

    try:
        with conectar() as con:
            cursor = con.cursor()
            cursor.execute(sql, (
                int(dados["id_curso"]),
                int(dados["id_disciplina"]),
                int(dados["id_professor"]),
                dados["dia_semana"],
                dados["turno"],
                int(dados["qtd_vagas"])
            ))
            con.commit()
            return cursor.lastrowid

    except sqlite3.IntegrityError:
        raise ValueError(
            "Não foi possível cadastrar a turma. "
            "Verifique se esse professor já possui aula nesse dia e turno."
        )

def buscar_horarios_turmas(ids_turmas):
    if not ids_turmas:
        raise ValueError("Informe ao menos uma turma.")

    placeholders = ",".join("?" for _ in ids_turmas)

    sql = f"""
        SELECT id_turma, dia_semana, turno
        FROM turma
        WHERE id_turma IN ({placeholders})
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, [int(id_turma) for id_turma in ids_turmas])
        resultados = cursor.fetchall()

    horarios = {
        int(id_turma): {
            "dia_semana": dia_semana,
            "turno": turno
        }
        for id_turma, dia_semana, turno in resultados
    }

    ids_nao_encontrados = [
        id_turma
        for id_turma in ids_turmas
        if int(id_turma) not in horarios
    ]

    if ids_nao_encontrados:
        raise ValueError(f"Turma(s) não encontrada(s): {ids_nao_encontrados}")

    return horarios

def validar_conflito_horario_turmas_selecionadas(ids_turmas):
    horarios = buscar_horarios_turmas(ids_turmas)
    horarios_ocupados = {}

    for id_turma in ids_turmas:
        id_turma = int(id_turma)

        dia_semana = horarios[id_turma]["dia_semana"]
        turno = horarios[id_turma]["turno"]

        chave_horario = (
            normalizar_texto(dia_semana).casefold(),
            normalizar_texto(turno).casefold()
        )

        if chave_horario in horarios_ocupados:
            turma_conflitante = horarios_ocupados[chave_horario]

            raise ValueError(
                f"Conflito de horário: as turmas {turma_conflitante} e {id_turma} "
                f"acontecem em {dia_semana} no turno {turno}."
            )

        horarios_ocupados[chave_horario] = id_turma

    return True

def validar_conflito_horario_aluno(cursor, id_aluno, ids_turmas_novas):
    if not ids_turmas_novas:
        return True

    placeholders_novas = ",".join("?" for _ in ids_turmas_novas)
    placeholders_excluir = ",".join("?" for _ in ids_turmas_novas)

    sql = f"""
        SELECT
            t_nova.id_turma,
            t_nova.dia_semana,
            t_nova.turno,
            t_existente.id_turma
        FROM turma t_nova
        JOIN turma t_existente
            ON TRIM(t_existente.dia_semana) COLLATE NOCASE =
               TRIM(t_nova.dia_semana) COLLATE NOCASE
           AND TRIM(t_existente.turno) COLLATE NOCASE =
               TRIM(t_nova.turno) COLLATE NOCASE
        JOIN matricula_turma mt
            ON mt.id_turma = t_existente.id_turma
        JOIN matricula m
            ON m.id_matricula = mt.id_matricula
        WHERE m.id_aluno = ?
          AND m.data_cancelamento IS NULL
          AND t_nova.id_turma IN ({placeholders_novas})
          AND t_existente.id_turma NOT IN ({placeholders_excluir})
        LIMIT 1
    """

    parametros = (
        [int(id_aluno)] +
        [int(id_turma) for id_turma in ids_turmas_novas] +
        [int(id_turma) for id_turma in ids_turmas_novas]
    )

    cursor.execute(sql, parametros)
    conflito = cursor.fetchone()

    if conflito is not None:
        id_turma_nova, dia_semana, turno, id_turma_existente = conflito

        raise ValueError(
            f"Conflito de horário: a turma {id_turma_nova} acontece em "
            f"{dia_semana} no turno {turno}, mesmo horário da turma "
            f"{id_turma_existente}, que já está vinculada ao aluno."
        )

    return True

def inserir_matricula(dados):
    validar_id_obrigatorio("aluno", dados["id_aluno"], "Aluno")

    ids_turmas = extrair_ids_turmas(dados["ids_turmas"])
    valores_turmas = buscar_valores_turmas(ids_turmas)

    validar_conflito_horario_turmas_selecionadas(ids_turmas)

    id_aluno = int(dados["id_aluno"])

    for id_turma in ids_turmas:
        if not turma_tem_vaga(id_turma):
            raise ValueError(f"A turma {id_turma} não possui vagas disponíveis.")

    bolsista = dados["bolsista"]

    if bolsista == "Não":
        dados["perc_bolsa"] = "0"

    perc_bolsa = validar_dados_matricula_banco(
        dados["data_matricula"],
        bolsista,
        dados["perc_bolsa"]
    )

    try:
        with conectar() as con:
            cursor = con.cursor()

            cursor.execute("""
                SELECT id_matricula
                FROM matricula
                WHERE id_aluno = ?
                  AND data_cancelamento IS NULL
                LIMIT 1
            """, (id_aluno,))

            resultado = cursor.fetchone()

            if resultado is None:
                cursor.execute("""
                    INSERT INTO matricula (
                        id_aluno,
                        data_matricula,
                        bolsista,
                        perc_bolsa,
                        data_cancelamento
                    )
                    VALUES (?, ?, ?, ?, NULL)
                """, (
                    id_aluno,
                    dados["data_matricula"],
                    bolsista,
                    perc_bolsa
                ))

                id_matricula = cursor.lastrowid

            else:
                id_matricula = resultado[0]

                cursor.execute("""
                    UPDATE matricula
                    SET bolsista = ?,
                        perc_bolsa = ?
                    WHERE id_matricula = ?
                      AND data_cancelamento IS NULL
                """, (
                    bolsista,
                    perc_bolsa,
                    id_matricula
                ))

            for id_turma in ids_turmas:
                cursor.execute("""
                    SELECT 1
                    FROM matricula_turma
                    WHERE id_matricula = ?
                      AND id_turma = ?
                    LIMIT 1
                """, (
                    id_matricula,
                    id_turma
                ))

                if cursor.fetchone() is not None:
                    raise ValueError(
                        f"Essa matrícula já está vinculada à turma {id_turma}."
                    )

                validar_conflito_horario_aluno(
                    cursor,
                    id_aluno,
                    ids_turmas
            )

            for id_turma in ids_turmas:
                cursor.execute("""
                    INSERT INTO matricula_turma (
                        id_matricula,
                        id_turma,
                        valor_mensalidade
                    )
                    VALUES (?, ?, ?)
                """, (
                    id_matricula,
                    id_turma,
                    valores_turmas[id_turma]
                ))

            con.commit()
            return id_matricula

    except sqlite3.IntegrityError as erro:
        raise ValueError(f"Erro ao cadastrar matrícula: {erro}")

def inserir_professor_com_academico(dados_professor, dados_acad):
    cpf = somente_numeros(dados_professor["cpf"])

    validar_cpf_mesma_pessoa(
        cpf=cpf,
        nome=dados_professor["nome"],
        tipo_cadastro="professor"
    )

    sql_professor = """
        INSERT INTO professor (
            nome,
            data_nasc,
            cpf,
            cep,
            rua,
            bairro,
            cidade,
            uf,
            telefone,
            email,
            sexo
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    valores_professor = (
        dados_professor["nome"],
        dados_professor["data_nasc"],
        cpf,
        somente_numeros(dados_professor["cep"]),
        dados_professor["rua"],
        dados_professor["bairro"],
        dados_professor["cidade"],
        dados_professor["uf"],
        somente_numeros(dados_professor["telefone"]),
        dados_professor["email"],
        dados_professor["sexo"]
    )

    sql_acad = """
        INSERT INTO dados_acad_prof (
            id_professor,
            instituicao,
            curso,
            grau,
            data_inicio,
            data_fim
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """

    try:
        with conectar() as con:
            cursor = con.cursor()

            cursor.execute(sql_professor, valores_professor)
            id_professor = cursor.lastrowid

            cursor.execute(sql_acad, (
                id_professor,
                dados_acad["instituicao"],
                dados_acad["curso"],
                dados_acad["grau"],
                dados_acad["data_inicio"],
                dados_acad["data_fim"]
            ))

            con.commit()
            return id_professor

    except sqlite3.IntegrityError as erro:
        raise ValueError(f"Erro ao cadastrar professor: {erro}")

TABELAS_IDS = {
    "aluno": "id_aluno",
    "professor": "id_professor",
    "curso": "id_curso",
    "disciplina": "id_disciplina",
    "turma": "id_turma",
    "matricula": "id_matricula",
}

def id_existe(tabela, valor_id):
    if tabela not in TABELAS_IDS:
        raise ValueError(f"Tabela não permitida: {tabela}")

    if not str(valor_id).strip().isdigit():
        return False

    campo_id = TABELAS_IDS[tabela]

    sql = f"""
        SELECT 1
        FROM {tabela}
        WHERE {campo_id} = ?
        LIMIT 1
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (int(valor_id),))
        return cursor.fetchone() is not None

def validar_id_obrigatorio(tabela, valor_id, nome_campo):
    if not id_existe(tabela, valor_id):
        raise ValueError(f"{nome_campo} não encontrado no banco.")

def executar_select(sql, params=()):
    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()

def montar_where(mapa_filtros, filtro, termo):
    termo = (termo or "").strip()

    if not termo:
        return "", []

    if filtro not in mapa_filtros:
        raise ValueError(f"Filtro inválido: {filtro}")

    coluna, tipo = mapa_filtros[filtro]

    if tipo == "id":
        if not termo.isdigit():
            raise ValueError("Para buscar por ID, digite apenas números.")
        return f" WHERE {coluna} = ? ", [int(termo)]

    return f" WHERE {coluna} LIKE ? ", [f"%{termo}%"]

def consultar_alunos(filtro, termo):
    mapa = {
        "ID": ("id_aluno", "id"),
        "Nome": ("nome", "texto"),
        "CPF": ("cpf", "texto"),
        "Telefone": ("telefone", "texto"),
    }

    where, params = montar_where(mapa, filtro, termo)

    sql = f"""
        SELECT
            id_aluno,
            nome,
            cpf,
            telefone
        FROM aluno
        {where}
        ORDER BY nome
    """

    return executar_select(sql, params)

def consultar_professores(filtro, termo):
    mapa = {
        "ID": ("id_professor", "id"),
        "Nome": ("nome", "texto"),
        "CPF": ("cpf", "texto"),
        "Telefone": ("telefone", "texto"),
    }

    where, params = montar_where(mapa, filtro, termo)

    sql = f"""
        SELECT
            id_professor,
            nome,
            cpf,
            telefone
        FROM professor
        {where}
        ORDER BY nome
    """

    return executar_select(sql, params)

def consultar_disciplinas(filtro, termo):
    mapa = {
        "ID": ("d.id_disciplina", "id"),
        "Nome da Disciplina": ("d.nome_disciplina", "texto"),
        "Curso": ("c.nome_curso", "texto"),
        "Professor": ("p.nome", "texto"),
    }

    where, params = montar_where(mapa, filtro, termo)

    sql = f"""
        SELECT
            d.id_disciplina,
            d.nome_disciplina,
            COALESCE(GROUP_CONCAT(DISTINCT c.nome_curso), '') AS cursos,
            COALESCE(GROUP_CONCAT(DISTINCT p.nome), '') AS professores
        FROM disciplina d

        LEFT JOIN curso_disciplina cd
            ON cd.id_disciplina = d.id_disciplina

        LEFT JOIN curso c
            ON c.id_curso = cd.id_curso

        LEFT JOIN turma t
            ON t.id_disciplina = d.id_disciplina

        LEFT JOIN professor p
            ON p.id_professor = t.id_professor

        {where}

        GROUP BY
            d.id_disciplina,
            d.nome_disciplina

        ORDER BY d.nome_disciplina
    """

    return executar_select(sql, params)

def consultar_cursos(filtro, termo):
    mapa = {
        "ID": ("c.id_curso", "id"),
        "Nome do Curso": ("c.nome_curso", "texto"),
        "Nome do curso": ("c.nome_curso", "texto"),
        "Turma": ("t.id_turma", "id"),
        "Aluno": ("a.nome", "texto"),
    }

    where, params = montar_where(mapa, filtro, termo)

    sql = f"""
        SELECT
            c.id_curso,
            c.nome_curso,
            COALESCE(GROUP_CONCAT(DISTINCT t.id_turma), '') AS turmas,

            COUNT(DISTINCT CASE
                WHEN m.data_cancelamento IS NULL
                THEN a.id_aluno
            END) AS alunos_matriculados

        FROM curso c

        LEFT JOIN turma t
            ON t.id_curso = c.id_curso

        LEFT JOIN matricula_turma mt
            ON mt.id_turma = t.id_turma

        LEFT JOIN matricula m
            ON m.id_matricula = mt.id_matricula

        LEFT JOIN aluno a
            ON a.id_aluno = m.id_aluno

        {where}

        GROUP BY
            c.id_curso,
            c.nome_curso

        ORDER BY c.nome_curso
    """

    return executar_select(sql, params)

def consultar_turmas(filtro, termo):
    mapa = {
        "ID": ("t.id_turma", "id"),
        "ID Turma": ("t.id_turma", "id"),
        "Curso": ("c.nome_curso", "texto"),
        "Disciplina": ("d.nome_disciplina", "texto"),
        "Professor": ("p.nome", "texto"),
        "Dia da Semana": ("t.dia_semana", "texto"),
        "Turno": ("t.turno", "texto"),
    }

    where, params = montar_where(mapa, filtro, termo)

    sql = f"""
        SELECT
            t.id_turma,
            d.nome_disciplina,
            c.nome_curso,
            p.nome,
            t.dia_semana,
            t.turno,
            t.qtd_vagas,
            COUNT(DISTINCT m.id_matricula) AS matriculados
        FROM turma t
        JOIN curso c
            ON c.id_curso = t.id_curso
        JOIN disciplina d
            ON d.id_disciplina = t.id_disciplina
        JOIN professor p
            ON p.id_professor = t.id_professor
        LEFT JOIN matricula_turma mt
            ON mt.id_turma = t.id_turma
        LEFT JOIN matricula m
            ON m.id_matricula = mt.id_matricula
           AND m.data_cancelamento IS NULL
        {where}
        GROUP BY
            t.id_turma,
            d.nome_disciplina,
            c.nome_curso,
            p.nome,
            t.dia_semana,
            t.turno,
            t.qtd_vagas
        ORDER BY t.id_turma
    """

    return executar_select(sql, params)

def consultar_matriculas(filtro, termo):
    termo = (termo or "").strip()

    mapa = {
        "ID Matrícula": ("m.id_matricula", "id"),
        "ID Aluno": ("a.id_aluno", "id"),
        "ID Turma": ("t.id_turma", "id"),
        "Nome": ("a.nome", "texto"),
        "CPF": ("a.cpf", "texto"),
        "Curso": ("c.nome_curso", "texto"),
        "Bolsista": ("m.bolsista", "texto"),
    }

    if filtro == "Status" and termo:
        status = termo.lower()

        if status.startswith("ati"):
            where = " WHERE m.data_cancelamento IS NULL "
            params = []
        elif status.startswith("can"):
            where = " WHERE m.data_cancelamento IS NOT NULL "
            params = []
        else:
            raise ValueError("Para Status, digite Ativa ou Cancelada.")
    else:
        where, params = montar_where(mapa, filtro, termo)

    sql = f"""
        SELECT
            m.id_matricula,
            a.nome,
            a.cpf,
            GROUP_CONCAT(DISTINCT c.nome_curso) AS cursos,
            GROUP_CONCAT(DISTINCT t.id_turma) AS turmas,
            m.bolsista,
            m.perc_bolsa,

            COALESCE(SUM(mt.valor_mensalidade), 0) AS valor_sem_desconto,

            CASE
                WHEN m.bolsista = 'Sim'
                THEN ROUND(
                    COALESCE(SUM(mt.valor_mensalidade), 0)
                    - (
                        COALESCE(SUM(mt.valor_mensalidade), 0)
                        * m.perc_bolsa / 100
                    ),
                    2
                )
                ELSE COALESCE(SUM(mt.valor_mensalidade), 0)
            END AS mensalidade_final,

            CASE
                WHEN m.data_cancelamento IS NULL THEN 'Ativa'
                ELSE 'Cancelada'
            END AS status

        FROM matricula m

        JOIN aluno a
            ON a.id_aluno = m.id_aluno

        LEFT JOIN matricula_turma mt
            ON mt.id_matricula = m.id_matricula

        LEFT JOIN turma t
            ON t.id_turma = mt.id_turma

        LEFT JOIN curso c
            ON c.id_curso = t.id_curso

        {where}

        GROUP BY
            m.id_matricula,
            a.nome,
            a.cpf,
            m.bolsista,
            m.perc_bolsa,
            m.data_cancelamento

        ORDER BY m.id_matricula DESC
    """

    return executar_select(sql, params)

def cancelar_matricula(id_matricula, data_cancelamento):
    id_matricula = str(id_matricula).strip()
    data_cancelamento = str(data_cancelamento).strip()

    if not id_matricula:
        raise ValueError("Informe o ID da matrícula.")

    if not id_matricula.isdigit():
        raise ValueError("O ID da matrícula deve conter apenas números.")

    if not data_cancelamento:
        raise ValueError("Informe a data de cancelamento.")

    data_cancelamento_convertida = converter_data_br(
        data_cancelamento,
        "Data de cancelamento"
    )

    hoje = dt.now().date()

    if data_cancelamento_convertida > hoje:
        raise ValueError("A data de cancelamento não pode ser futura.")

    sql_verificar = """
        SELECT data_matricula, data_cancelamento
        FROM matricula
        WHERE id_matricula = ?
    """

    sql_cancelar = """
        UPDATE matricula
        SET data_cancelamento = ?
        WHERE id_matricula = ?
          AND data_cancelamento IS NULL
    """

    with conectar() as con:
        cursor = con.cursor()

        cursor.execute(sql_verificar, (int(id_matricula),))
        resultado = cursor.fetchone()

        if resultado is None:
            raise ValueError("Matrícula não encontrada.")

        data_matricula, data_cancelamento_atual = resultado

        if data_cancelamento_atual is not None:
            raise ValueError("Essa matrícula já está cancelada.")

        data_matricula_convertida = converter_data_br(
            data_matricula,
            "Data de matrícula"
        )

        if data_cancelamento_convertida < data_matricula_convertida:
            raise ValueError(
                "A data de cancelamento não pode ser anterior à data de matrícula."
            )

        cursor.execute(sql_cancelar, (data_cancelamento, int(id_matricula)))
        con.commit()

        if cursor.rowcount == 0:
            raise ValueError("Não foi possível cancelar a matrícula.")

        return True

def extrair_ids_turmas(texto_ids):
    texto_ids = str(texto_ids).strip()

    if not texto_ids:
        raise ValueError("Informe ao menos uma turma.")

    partes = texto_ids.replace(";", ",").split(",")

    ids_turmas = []
    ids_repetidos = set()

    for parte in partes:
        parte = parte.strip()

        if not parte:
            continue

        if not parte.isdigit():
            raise ValueError("Digite os IDs das turmas separados por vírgula. Exemplo: 1,2,3")

        id_turma = int(parte)

        if id_turma in ids_turmas:
            ids_repetidos.add(id_turma)

        ids_turmas.append(id_turma)

    if ids_repetidos:
        raise ValueError(f"Turma repetida no campo: {sorted(ids_repetidos)}")

    if not ids_turmas:
        raise ValueError("Informe ao menos uma turma.")

    return ids_turmas

def buscar_valores_turmas(ids_turmas):
    if not ids_turmas:
        raise ValueError("Informe ao menos uma turma.")

    placeholders = ",".join("?" for _ in ids_turmas)

    sql = f"""
        SELECT
            t.id_turma,
            cd.valor_mensalidade
        FROM turma t
        JOIN curso_disciplina cd
            ON cd.id_curso = t.id_curso
           AND cd.id_disciplina = t.id_disciplina
        WHERE t.id_turma IN ({placeholders})
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, ids_turmas)
        resultados = cursor.fetchall()

    valores = {
        int(id_turma): float(valor)
        for id_turma, valor in resultados
    }

    ids_nao_encontrados = [
        id_turma
        for id_turma in ids_turmas
        if id_turma not in valores
    ]

    if ids_nao_encontrados:
        raise ValueError(
            f"Turma(s) não encontrada(s) ou sem valor de disciplina vinculado: {ids_nao_encontrados}"
        )

    return valores

def calcular_total_turmas(texto_ids):
    ids_turmas = extrair_ids_turmas(texto_ids)
    valores = buscar_valores_turmas(ids_turmas)

    total = sum(valores[id_turma] for id_turma in ids_turmas)

    return total

def listar_cursos_combo():
    sql = """
        SELECT id_curso, nome_curso
        FROM curso
        ORDER BY nome_curso
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

def buscar_aluno_por_id(id_aluno):
    if not str(id_aluno).strip().isdigit():
        raise ValueError("ID do aluno inválido.")

    sql = """
        SELECT nome
        FROM aluno
        WHERE id_aluno = ?
        LIMIT 1
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (int(id_aluno),))
        resultado = cursor.fetchone()

    if resultado is None:
        return None

    return resultado[0]

def buscar_professor_por_id(id_professor):
    if not str(id_professor).strip().isdigit():
        raise ValueError("ID do professor inválido.")

    sql = """
        SELECT nome
        FROM professor
        WHERE id_professor = ?
        LIMIT 1
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (int(id_professor),))
        resultado = cursor.fetchone()

    if resultado is None:
        return None

    return resultado[0]

def normalizar_texto_comparacao(valor):
    valor = " ".join(str(valor).strip().split())

    valor_sem_acento = unicodedata.normalize("NFD", valor)
    valor_sem_acento = "".join(
        char for char in valor_sem_acento
        if unicodedata.category(char) != "Mn"
    )

    return valor_sem_acento.casefold()

def buscar_valor_curso_disciplina(id_curso, id_disciplina):
    sql = """
        SELECT valor_mensalidade
        FROM curso_disciplina
        WHERE id_curso = ?
          AND id_disciplina = ?
        LIMIT 1
    """

    with conectar() as con:
        cursor = con.cursor()
        cursor.execute(sql, (int(id_curso), int(id_disciplina)))
        resultado = cursor.fetchone()

    if resultado is None:
        raise ValueError("Valor da disciplina não encontrado para esse curso.")

    return float(resultado[0])


# ============================================================
# VALIDAÇÕES E MÉTODOS DE APOIO
# Arquivo original: validacoes(23).py
# ============================================================

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


# ============================================================
# TELA DE DADOS ACADÊMICOS DO PROFESSOR
# Arquivo original: dados_acad_prof(13).py
# ============================================================

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


# ============================================================
# TELA DE ALUNO
# Arquivo original: aluno(12).py
# ============================================================

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


# ============================================================
# TELA DE CURSO
# Arquivo original: curso(12).py
# ============================================================

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


# ============================================================
# TELA DE DISCIPLINA
# Arquivo original: disciplina(13).py
# ============================================================

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


# ============================================================
# TELA DE TURMA
# Arquivo original: turma(11).py
# ============================================================

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


# ============================================================
# TELA DE MATRÍCULA
# Arquivo original: matricula(15).py
# ============================================================

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


# ============================================================
# TELA DE PROFESSOR
# Arquivo original: professor(11).py
# ============================================================

class JanelaProfessor(ctk.CTkFrame, validacoes):
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

        self.label_dica_busca = ctk.CTkLabel(self.frame, text="Digite sua consulta", text_color="#B5B2CA", font=("Arial", 10))
        self.label_dica_busca.grid(row=2, column=2, padx=5, sticky="w")
        self.configurar_validacao_consulta()

        self.btn_buscar = ctk.CTkButton(self.frame, text="🔍", width=40, command=self.consultar_professor)
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

    def consultar_professor(self):
        try:
            if not self.validar_termo_busca_consulta():
                return

            dados = consultar_professores(
                self.filtro_busca_consulta(),
                self.termo_busca_consulta()
            )

            self.tratar_resultado_consulta(dados, "professor")

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

        ctk.CTkLabel(self.frame, text= 'CADASTRO DE DADOS PESSOAIS DO PROFESSOR', font= ('IMPACT', 30), text_color= '#B5B2CA').grid(row= 0, column= 0, columnspan= 2, pady= 20)

        ctk.CTkLabel(self.frame, text= 'ID_Professor', font=('IMPACT', 14), text_color="#B5B2CA").grid(row=1, column=0, padx= 10, sticky='ew')
        self.entry_id_prof = ctk.CTkEntry(self.frame,fg_color="#787879")
        self.entry_id_prof.grid(row=1, column=1,padx= 5, pady= 10, sticky='w')
        self.entry_id_prof.insert(0, ' ')
        self.entry_id_prof.configure(state= 'readonly')

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
        self.entry_CPF.bind("<KeyRelease>", self.formatar_CPF_digitando)
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

        self.label_sucesso = ctk.CTkLabel(self.frame, text=" ", text_color="green", font=("IMPACT", 22))
        self.label_sucesso.grid(row=20, column=0, columnspan=2, pady=5, padx=20)
        self.label_sucesso.configure(text= ' ')

        ctk.CTkButton(
            self.frame,
            text='DADOS ACADÊMICOS DO PROFESSOR',
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
            messagebox.showerror('Erro', 'Todos os campos devem ser preenchidos')
            return False

        Dados_acad_prof(self, self)


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


# ============================================================
# TELA DE LOGIN
# Arquivo original: login(9).py
# ============================================================

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

        self.erro_usuario.configure(text='')
        self.controller.abrir_janela(JanelaPrincipal)
        return True


# ============================================================
# TELA PRINCIPAL
# Arquivo original: principal(11).py
# ============================================================

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


# ============================================================
# ARQUIVO PRINCIPAL / INICIALIZAÇÃO
# Arquivo original: main(10).py
# ============================================================

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
