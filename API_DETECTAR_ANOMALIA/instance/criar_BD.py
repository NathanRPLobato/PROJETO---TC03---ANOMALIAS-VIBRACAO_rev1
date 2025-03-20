import sqlite3
import os

# Função para criar o banco de dados e tabelas
def criar_banco_e_tabela(caminho_bd, query_criacao):
    # Certificar que a pasta existe
    os.makedirs(os.path.dirname(caminho_bd), exist_ok=True)
    
    # Conectar ao banco e criar a tabela
    conn = sqlite3.connect(caminho_bd)
    cursor = conn.cursor()
    cursor.execute(query_criacao)
    print(f"Banco de dados configurado em: {caminho_bd}")
    conn.commit()
    conn.close()

# Caminhos dos bancos de dados
caminho_bd_raw = r"API_DETECTAR_ANOMALIA\instance\raw\dados_raw.db"
caminho_bd_refined = r"API_DETECTAR_ANOMALIA\instance\refined\dados_refined.db"

# Query de criação da tabela "dados_raw"
query_dados_raw = '''
CREATE TABLE IF NOT EXISTS dados_raw (
    x REAL,
    y REAL,
    z REAL
);
'''

# Query de criação da tabela "dados_refined"
query_dados_refined = '''
CREATE TABLE IF NOT EXISTS dados_refined (
    magnitude REAL,
    mean REAL,
    std REAL,
    kurt REAL,
    skewness REAL,
    fft_max_freq REAL
);
'''

criar_banco_e_tabela(caminho_bd_raw, query_dados_raw)
criar_banco_e_tabela(caminho_bd_refined, query_dados_refined)

print("Os dois bancos de dados foram criados com sucesso!")
