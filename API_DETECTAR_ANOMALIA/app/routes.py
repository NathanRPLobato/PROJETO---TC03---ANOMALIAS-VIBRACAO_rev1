from app.funcoesfft import realizar_fft, detectar_falha, obter_dados_fft
import pandas as pd
import numpy as np
import os
import joblib
from flask import Blueprint, Flask, request, jsonify
from flask_cors import CORS
from scipy.stats import kurtosis, skew
from scipy.fft import fft

# Função para carregar os modelos
def carregar_modelos():
    model_dir = "API_DETECTAR_ANOMALIA/models"
    modelo_knn = joblib.load(os.path.join(model_dir, "knn_model.pkl"))
    modelo_rf = joblib.load(os.path.join(model_dir, "rf_model.pkl"))
    scaler = joblib.load(os.path.join(model_dir, "scaler.pkl"))
    return modelo_knn, modelo_rf, scaler

modelo_knn, modelo_rf, scaler = carregar_modelos()

routes = Blueprint("routes", __name__)
CAMINHO_CSV_RAW = "API_DETECTAR_ANOMALIA/instance/raw/dados_coletados.csv"
CAMINHO_CSV_REFINED = "API_DETECTAR_ANOMALIA/instance/refined/dados_refined.csv"

# Função para configurar as rotas
def configurar_rotas(app):
    app.register_blueprint(routes)

# Rota de home
@routes.route("/", methods=["GET"])
def home():
    return "API de Coleta e Predição de Anomalias", 200

# Rota de coleta de dados
@routes.route("/collect", methods=["POST"])
def coletar_dados():
    try:
        dados_recebidos = request.get_json()
        if not dados_recebidos or "dados" not in dados_recebidos:
            return jsonify({"erro": "Dados inválidos ou ausentes"}), 400

        amostras = np.array(dados_recebidos["dados"])
        if amostras.ndim == 1:
            amostras = np.expand_dims(amostras, axis=0)
        df = pd.DataFrame(amostras)

        # Salvar os dados no arquivo raw (dados_coletados.csv)
        with open(CAMINHO_CSV_RAW, mode="a", newline="", encoding="utf-8") as f:
            df.to_csv(f, header=f.tell() == 0, index=False)

        # Criar as features adicionais: magnitude e máxima frequência da FFT
        magnitude = np.sqrt(df.iloc[:, 0]**2 + df.iloc[:, 1]**2 + df.iloc[:, 2]**2)  # Magnitude do vetor de vibração
        fft_max_freq = np.array([np.max(np.abs(np.fft.fft(df.iloc[i, :], axis=0))) for i in range(df.shape[0])])  # Máxima amplitude da FFT (análise no domínio da frequência)
        mean = df.mean(axis=1)  # Média dos valores
        std = df.std(axis=1)  # Desvio padrão
        kurt = kurtosis(df, axis=1, nan_policy='omit')  # Curtose (avalia extremidades da distribuição)
        skewness = skew(df, axis=1, nan_policy='omit')  # Assimetria dos dados

        # Empilhar as novas features magnitude, mean, std, kurt, skewness, fft_max_freq
        features = np.column_stack([magnitude, mean, std, kurt, skewness, fft_max_freq])

        # Criar o DataFrame com as novas features
        dados_refinados = pd.DataFrame(features, columns=["magnitude", "mean", "std", "kurt", "skewness", "fft_max_freq"])

        # Verifica se o arquivo refined existe, caso contrário, cria o arquivo com cabeçalho
        if not os.path.exists(CAMINHO_CSV_REFINED):
            dados_refinados.to_csv(CAMINHO_CSV_REFINED, index=False)
        else:
            dados_refinados.to_csv(CAMINHO_CSV_REFINED, mode="a", header=False, index=False)

        return jsonify({"mensagem": "Dados coletados e salvos com sucesso!"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
# Rota de previsão
@routes.route("/predict", methods=["GET"])
def prever():
    try:
        dados = pd.read_csv(CAMINHO_CSV_REFINED)

        ultimas_amostras = dados.tail(1).values
        ultimas_amostras_transformadas = scaler.transform(ultimas_amostras)

        pred_knn = modelo_knn.predict(ultimas_amostras_transformadas)
        pred_rf = modelo_rf.predict(ultimas_amostras_transformadas)

        resultado = {
            "amostras_utilizadas": ultimas_amostras.tolist(),
            "resultado_knn": pred_knn.tolist(),
            "resultado_rf": pred_rf.tolist(),
            "classificacao": [
                "falha critica" if r == "falha critica" else "falha tendencial" if r == "falha tendencial" else "operacao normal"
                for r in pred_rf.tolist()
            ]
        }
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# Rota de FFT
@routes.route("/fft", methods=["GET"])
def fft():
    try:
        # Carregar as últimas 60 linhas do CSV
        df = pd.read_csv(CAMINHO_CSV_RAW)
        df_ultimas_60 = df.tail(60)  # Pega as últimas 60 linhas

        # Verificar se as últimas 60 linhas têm dados válidos
        if df_ultimas_60.isnull().values.any():
            return jsonify({"erro": "Dados inválidos nas últimas 60 linhas do CSV"}), 400

        # Garantir que os dados de X, Y, Z sejam numéricos
        df_ultimas_60 = df_ultimas_60.apply(pd.to_numeric, errors='coerce')

        # Verificar se ainda há valores inválidos
        if df_ultimas_60.isnull().values.any():
            return jsonify({"erro": "Dados inválidos ou não numéricos nas últimas 60 linhas do CSV"}), 400

        # Exibir para diagnóstico os dados das últimas 60 linhas
        print("Últimas 60 linhas: ", df_ultimas_60)

        # Realizar FFT nos dados de vibração (eixos X, Y, Z)
        fft_results = realizar_fft(df_ultimas_60)  # Usa as últimas 60 linhas para FFT
        
        # Exibir para diagnóstico os resultados da FFT
        print("Resultados da FFT: ", fft_results)

        # Obter os dados necessários para o gráfico em formato JSON
        fft_dados = obter_dados_fft(fft_results)

        # Análise de falha com base nas frequências
        falhas = {}
        for eixo, dados_fft in fft_results.items():
            frequencias = dados_fft['frequencias']
            espectro = dados_fft['espectro']
            
            # Verificar se o espectro não está vazio
            if espectro.size == 0:
                return jsonify({"erro": f"Espectro vazio para o eixo {eixo}"}), 400
            
            # Identificar pico de frequência
            pico_frequencia = frequencias[np.argmax(espectro)]
            tipo_falha = detectar_falha(pico_frequencia)
            
            falhas[eixo] = {
                'pico_frequencia': pico_frequencia,
                'tipo_falha': tipo_falha
            }

        # Salvar os resultados no arquivo CSV (dados_fft.csv)
        dados_fft_df = pd.DataFrame(falhas).T
        if not os.path.exists("API_DETECTAR_ANOMALIA/instance/refined/dados_fft.csv"):
            dados_fft_df.to_csv("API_DETECTAR_ANOMALIA/instance/refined/dados_fft.csv", index=True)
        else:
            dados_fft_df.to_csv("API_DETECTAR_ANOMALIA/instance/refined/dados_fft.csv", mode="a", header=False)

        # Preparar resposta em JSON
        resultado = {
            "fft_dados": fft_dados,
            "falhas_detectadas": falhas
        }
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


# Executar o servidor
if __name__ == "__main__":
    app = Flask(__name__)
    CORS(app)
    configurar_rotas(app)
    app.run(host="0.0.0.0", port=8000, debug=True)
