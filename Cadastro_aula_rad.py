#CADASTRO

#Cadastro de Aluno

#bibiotecas
from datetime import datetime
import requests


print('Cadastro do Aluno')

def Aluno():
    while True:
        nome = input('Digite o nome completo do aluno.\n').strip()
        if not nome:#---------------------------------------------------------------------nome
            print('Campo obrigatório.\n')
        elif any(char.isdigit() for char in nome):
            print('Este campo não deve conter números.\n')
        elif len(nome) < 10:
            print('Nome inválido.\n')
        elif nome.isdigit():
            print('Caracter inválido.\n')
        else:
            break
    while True:#-----------------------------------------------------------------------cpf
        cpf = input('Digite o CPF do aluno').strip()
        if not cpf:
            print('Campo obrigatório.\n')
        elif len(cpf) != 11:
            print('O CPF deve ter 11 dígitos.\n')
        elif not cpf.isdigit():
            print('Digite apenas números')
        else:
            break
    while True:#--------------------------------------------------------------------------sexo
        sexo_aluno = ['Masculino', 'masculino', 'Feminino', 'feminino', 'Outro', 'outro']
        entrada = input('Sexo:\n').strip()
        if not entrada:
            print('Campo obrigatório.\n')
        elif entrada not in sexo_aluno:
            print('Entrada Inválida.')
        elif entrada.isdigit():
            print('Entrada inválida.')
        else:
            break
    while True:#---------------------------------------------email
        entrada = input('Email:\n').strip()
        if not entrada:
            print('Campo obrigatório.\n')
        elif not entrada.islower() or "@" not in entrada:
            print('Email inválido')
        elif len(entrada) < 5:
            print('Email muito pequeno.\n')
        else:
            break
    while True:#---------------------------------------------data de nascimento
        data_nasc = input('Data de nascimento:\n').strip()

        if not data_nasc:
            print('Campo obrigatório.\n')
            continue
        try:
            data = datetime.strptime(data_nasc, "%d/%m/%Y")
            break
        except ValueError:
            print('Data inválida.\n')
            break
    while True:#-----------------------------------------------cep
        cep = input("Digite o CEP (somente números): ").strip()
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
        elif any(char.isalpha() for char in cep):
            print('CEP inválido.\n')
        elif len(cep) != 8:
            print('O cep deve conter 8 dígitos')
        elif not cep.isdigit:
            print('Digite apenas números')
        else:
            print("Erro na requisição.")
            break
    while True:
        telefone = input('Telefone para contato(DDD-999999999):\n').strip()
        if not telefone:
            print('Campo obrigatório.\n')
        elif not telefone.isdigit():
            print('Digite apenas números.\n')
        elif len(telefone) != 12:
            print('Digite um número de telefone válido.\n')
        else:
            return telefone


print('Cadastro da turma')


def turma():
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

        


print('Cadastro de Disciplinas')


def nome_disciplina():
    while True:
        nome = input('Nome da Disciplina:\n')
        if not nome:
            print('Campo obrigatório.\n')
        elif nome.isdigit():
            print('Não são permitidos números neste campo.\n')
        else:
            break
    while True:
        numero = input('Digite o Número da Disciplina:\n')                             
        if not numero.isdigit():                                                        
            print('Digite apenas números.\n')                                           
        elif len(numero) != 4:
            print('Número inválido.\n')
        else:
            return int(numero)