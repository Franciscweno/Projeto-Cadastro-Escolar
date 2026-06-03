import sqlite3
import os
import sys
import unicodedata
from datetime import datetime as dt

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