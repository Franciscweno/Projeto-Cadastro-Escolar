from datetime import datetime
import requests

def Validar_Nome():
    while True:
        nome = input('Digite seu nome completo.\n').strip()
        if not nome:
            print('Campo obrigatório.\n')
        elif any(char.isdigit() for char in nome):
            print('Este campo não deve conter números.\n')
        elif len(nome) < 10:
            print('Nome inválido.\n')
        else:
            return nome
        
def Validar_CPF():
    while True:
        cpf = input('Digite o CPF do aluno\n').strip()
        if not cpf:
            print('Campo obrigatório.\n')
        elif len(cpf) != 11:
            print('O CPF deve ter 11 dígitos.\n')
        elif not cpf.isdigit():
            print('Digite apenas números')
        else:
            return cpf
        
def Validar_Email():
    while True:
        entrada = input('Email:\n').strip()
        if not entrada:
            print('Campo obrigatório.\n')
        elif not entrada.islower() or "@" not in entrada:
            print('Email inválido')
        elif len(entrada) < 5:
            print('Email muito pequeno.\n')
        else:
            return entrada

def Validar_Sexo():
    while True:
        sexo = ['masculino', 'feminino', 'outro']
        entrada = input('Sexo:\n').strip().lower()
        if not entrada:
            print('Campo obrigatório.\n')
        elif entrada not in sexo:
            print('Entrada Inválida.')
        elif entrada.isdigit():
            print('Entrada inválida.')
        else:
            return entrada

def Validar_Data_Nasc():
    while True:
        data_nasc = input('Data de nascimento:(DD/MM/YYYY\n').strip()

        if not data_nasc:
            print('Campo obrigatório.\n')
            continue
        try:
            data = datetime.strptime(data_nasc, "%d/%m/%Y")
            break
        except ValueError:
            print('Data inválida.\n')
    return data.strftime('%d/%m/%Y')

def Validar_CEP():
    while True:
        cep = input("Digite o CEP (somente números): ").strip()
        if any(char.isalpha() for char in cep):
            print('CEP inválido.\n')
        elif len(cep) != 8:
            print('O cep deve conter 8 dígitos')
        elif not cep.isdigit():
            print('Digite apenas números')
        else:
            url = f"https://viacep.com.br/ws/{cep}/json/"
            resposta = requests.get(url)
            if resposta.status_code == 200:
                dados = resposta.json()
                if "erro" not in dados:
                    print("Logradouro:", dados["logradouro"])
                    print("Bairro:", dados["bairro"])
                    print("Cidade:", dados["localidade"])
                    print("Estado:", dados["uf"])
                else:
                    print("CEP não encontrado.")
            else:
                print("Erro ao acessar a API.")
            return cep
            
def Validar_Disciplina():
    while True:
        nome = input('Nome da Disciplina:\n')
        if not nome:
            print('Campo obrigatório.\n')
        elif nome.isdigit():
            print('Não são permitidos números neste campo.\n')
        elif len(nome) < 5:
            print('Nome inválido')
        else:
            break
    while True:
        numero = input('Digite o Número da Disciplina:\n')                             
        if not numero.isdigit():                                                        
            print('Digite apenas números.\n')                                           
        elif len(numero) != 4:
            print('Número inválido.\n')
        else:
            return nome, numero

def Validar_Turma():
    while True:
        turma_num = input('Digite o número da turma:\n')
        if not turma_num:
            print('Campo obrigatório.\n')
        elif len(turma_num) != 4:
            print('Digite um número válido.\n')
        elif not turma_num.isdigit():
            print('Digite apenas números.\n')
        else:
            return turma_num
        
nome = Validar_Nome()
CPF = Validar_CPF()
CEP = Validar_CEP()
Email = Validar_Email()
Disciplina_Nome, Disciplina_Num = Validar_Disciplina()
Turma = Validar_Turma()
Data_Nasc = Validar_Data_Nasc()

CAD = {'nome' :nome,
       'CPF' :CPF,
       'CEP': CEP,
       'Email': Email,
       'Disciplina': Disciplina_Nome,
       'Número da Disciplina':Disciplina_Num,
       'Turma': Turma,
       'Data de Nascimento': Data_Nasc}

print(CAD)