import numpy as np
from scipy.fft import fft

# Função para detectar o tipo de falha baseado na frequência
def detectar_falha(frequencia):
    # Associações de frequências com falhas típicas
    if 0.07 < frequencia < 10: # Limite inferior de 0.07 Hz para evitar falsos positivos
        return "Desbalanceamento"
    elif 10 <= frequencia < 100:
        return "Problema no Rolamento"
    elif 100 <= frequencia < 1000:
        return "Desgaste de Engrenagens"
    elif frequencia >= 1000:
        return "Falha de Alta Frequência"
    else:
        return "Falha Desconhecida"

# Função para calcular a FFT e gerar o espectro
def realizar_fft(dados):
    fft_results = {}
    for i, eixo in enumerate(['X', 'Y', 'Z']):
        # Realizar FFT para cada eixo de vibração
        yf = fft(dados.iloc[:, i])
        N = len(yf)
        freq = np.fft.fftfreq(N, d=1)  # Frequências associadas aos dados
        fft_results[eixo] = {
            'frequencias': freq[:N // 2],
            'espectro': np.abs(yf[:N // 2])
        }
    return fft_results

# Função para gerar os dados necessários para o gráfico de FFT
def obter_dados_fft(fft_results):
    fft_dados = {}
    for eixo, dados_fft in fft_results.items():
        fft_dados[eixo] = {
            'frequencias': dados_fft['frequencias'].tolist(),
            'espectro': dados_fft['espectro'].tolist()
        }
    return fft_dados