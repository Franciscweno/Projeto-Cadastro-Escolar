import pandas as pd
from faker import Faker
import os
import random

print(f"O arquivo será salvo em: {os.getcwd()}")

# Inicializa o gerador
fake = Faker('pt_BR')

# Lista de bairros fictícios
bairros = [
    "Centro", "Jardim América", "Setor Bueno", "Vila Nova",
    "Cidade Jardim", "Parque Amazônia", "Setor Oeste", "Setor Sul"
]

def gerar_base_contatos(nome_arquivo="clientes_original.xlsx", qtd=30):
    """Gera uma planilha com dados aleatórios brasileiros"""
    print(f"⏳ Gerando {qtd} registros... aguarde.")
    dados = []
    for _ in range(qtd):
        dados.append({
            "Nome": fake.name(),
            "Endereco": fake.street_address(),
            "CEP": fake.postcode(),
            "Bairro": random.choice(bairros),  # corrigido
            "Cidade": fake.city(),
            "Estado": fake.state_abbr(),
            "Telefone": fake.phone_number(),
            "Email": fake.email()
        })
    
    df = pd.DataFrame(dados)
    df.to_excel(nome_arquivo, index=False)
    print(f"✅ Arquivo '{nome_arquivo}' criado com sucesso!")

def processar_contatos(arquivo_entrada, arquivo_saida):
    """Lê um arquivo existente e aplica formatações"""
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Erro: O arquivo '{arquivo_entrada}' não foi encontrado!")
        return

    print(f"⏳ Processando dados de '{arquivo_entrada}'...")
    df = pd.read_excel(arquivo_entrada)
    
    # Exemplo de processamento: Nomes em maiúsculo e remoção de espaços extras
    df['Nome'] = df['Nome'].str.upper().str.strip()
    
    df.to_excel(arquivo_saida, index=False)
    print(f"✅ Processamento concluído! Salvo como: '{arquivo_saida}'")

# --- ÁREA DE EXECUÇÃO ---
# 1. Para gerar a base:
gerar_base_contatos("minha_base.xlsx", qtd=50)

# 2. Para processar (descomente a linha abaixo quando quiser usar):
# processar_contatos("minha_base.xlsx", "base_final_formatada.xlsx")