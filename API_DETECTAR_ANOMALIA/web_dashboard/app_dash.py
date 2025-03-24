from flask import Flask, render_template, jsonify
import requests
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# URLs das APIs
API_URL_PREDICTION = "http://192.168.0.111:8000/predict" # Alterar para o IP do seu servidor
API_URL_FFT = "http://192.168.0.111:8000/fft" # Alterar para o IP do seu servidor

def get_data():
    """Função para buscar os dados da API e gerar o gráfico."""
    # Consumir a API para obter os resultados de previsão
    response_prediction = requests.get(API_URL_PREDICTION)
    data_prediction = response_prediction.json() if response_prediction.status_code == 200 else {}

    # Extrair os resultados de KNN e RF com fallback para "Erro"
    resultado_knn = data_prediction.get("resultado_knn", ["Erro"])[0]
    resultado_rf = data_prediction.get("resultado_rf", ["Erro"])[0]

    # Consumir a API FFT para obter os dados de falha
    response_fft = requests.get(API_URL_FFT)
    data_fft = response_fft.json() if response_fft.status_code == 200 else {}

    # Verificar se a chave 'falhas_detectadas' existe no JSON retornado
    falha_detectada = "Equipamento Sem falha Evidente"
    if 'falhas_detectadas' in data_fft:
        for eixo in ['X', 'Y', 'Z']:
            if data_fft['falhas_detectadas'].get(eixo, {}).get('tipo_falha') not in [None, "Falha Desconhecida"]:
                falha_detectada = f"Falha no Eixo {eixo}: {data_fft['falhas_detectadas'][eixo]['tipo_falha']}"
                break

    # Definir as cores baseadas nos resultados
    knn_color = "green" if resultado_knn == "operacao normal" else "yellow" if resultado_knn == "falha potencial" else "blue" if resultado_knn == "sensor fora" else "red"
    rf_color = "green" if resultado_rf == "operacao normal" else "yellow" if resultado_rf == "falha potencial" else "blue" if resultado_rf == "sensor fora" else "red"

    """
    # Nova condição para status "Equipamento Desligado"
    if resultado_knn == "falha potencial" and resultado_rf == "falha potencial" and falha_detectada == "Equipamento Sem falha Evidente":
        knn_color = "blue"
        rf_color = "blue"
        resultado_knn = "Equipamento Desligado"
        resultado_rf = "Equipamento Desligado"
    """
    
    # Preparar os dados FFT para o gráfico
    frequencias = data_fft.get('fft_dados', {}).get('X', {}).get('frequencias', [])
    espectro_X = data_fft.get('fft_dados', {}).get('X', {}).get('espectro', [])
    espectro_Y = data_fft.get('fft_dados', {}).get('Y', {}).get('espectro', [])
    espectro_Z = data_fft.get('fft_dados', {}).get('Z', {}).get('espectro', [])

    # Gerar o gráfico FFT
    graph_img = None
    if frequencias and espectro_X and espectro_Y and espectro_Z:
        fig, ax = plt.subplots()
        ax.plot(frequencias, espectro_X, label='Eixo X', color='blue')
        ax.plot(frequencias, espectro_Y, label='Eixo Y', color='green')
        ax.plot(frequencias, espectro_Z, label='Eixo Z', color='red')
        ax.set_title('Gráfico FFT - Eixos X, Y, Z')
        ax.set_xlabel('Frequência (Hz)')
        ax.set_ylabel('Magnitude')
        ax.legend()
    
        img = io.BytesIO()
        fig.savefig(img, format='png')
        img.seek(0)
        graph_img = base64.b64encode(img.getvalue()).decode()

    return {
        "resultado_knn": resultado_knn,
        "resultado_rf": resultado_rf,
        "knn_color": knn_color,
        "rf_color": rf_color,
        "falha_detectada": falha_detectada,
        "graph_img": graph_img
    }

# Rota principal (renderiza o HTML)
@app.route("/")
def index():
    return render_template("index.html")

# Rota que retorna os dados para atualização dinâmica
@app.route("/data")
def data():
    return jsonify(get_data())

if __name__ == "__main__":
    app.run(debug=True)
