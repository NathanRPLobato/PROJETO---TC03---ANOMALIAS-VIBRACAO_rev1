from flask import Flask, render_template
import requests
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# URLs das APIs
API_URL_PREDICTION = "http://192.168.0.106:8000/predict"
API_URL_FFT = "http://192.168.0.106:8000/fft"

# Rota principal
@app.route("/")
def index():
    # Consumir a API para obter os resultados de previsão
    response_prediction = requests.get(API_URL_PREDICTION)
    data_prediction = response_prediction.json()

    # Extrair os resultados de KNN e RF
    resultado_knn = data_prediction.get("resultado_knn", ["Erro"])[0]
    resultado_rf = data_prediction.get("resultado_rf", ["Erro"])[0]

    # Definir as cores baseadas nos resultados
    knn_color = "green" if resultado_knn == "operacao normal" else "yellow" if resultado_knn == "falha potencial" else "red"
    rf_color = "green" if resultado_rf == "operacao normal" else "yellow" if resultado_rf == "falha potencial" else "red"

    # Consumir a API FFT para obter os dados de falha
    response_fft = requests.get(API_URL_FFT)
    data_fft = response_fft.json()

    # Verificar qual falha foi detectada nos eixos X, Y, Z
    falha_detectada = "Equipamento Sem falha Evidente"
    for eixo in ['X', 'Y', 'Z']:
        if data_fft['falhas_detectadas'][eixo]['tipo_falha'] != "Falha Desconhecida":
            falha_detectada = f"Falha no Eixo {eixo}: {data_fft['falhas_detectadas'][eixo]['tipo_falha']}"
            break

    # Preparar os dados FFT para o gráfico
    frequencias = data_fft['fft_dados']['X']['frequencias']
    espectro_X = data_fft['fft_dados']['X']['espectro']
    espectro_Y = data_fft['fft_dados']['Y']['espectro']
    espectro_Z = data_fft['fft_dados']['Z']['espectro']

    # Gerar o gráfico FFT
    fig, ax = plt.subplots()
    ax.plot(frequencias, espectro_X, label='Eixo X', color='blue')
    ax.plot(frequencias, espectro_Y, label='Eixo Y', color='green')
    ax.plot(frequencias, espectro_Z, label='Eixo Z', color='red')
    ax.set_title('Gráfico FFT - Eixos X, Y, Z')
    ax.set_xlabel('Frequência (Hz)')
    ax.set_ylabel('Magnitude')
    ax.legend()

    # Salvar o gráfico em uma imagem base64 para ser renderizada no HTML
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    graph_img = base64.b64encode(img.getvalue()).decode()

    # Passar os dados para o template HTML
    return render_template("index.html", resultado_knn=resultado_knn, resultado_rf=resultado_rf, 
                           knn_color=knn_color, rf_color=rf_color, falha_detectada=falha_detectada,
                           graph_img=graph_img)

if __name__ == "__main__":
    app.run(debug=True)
