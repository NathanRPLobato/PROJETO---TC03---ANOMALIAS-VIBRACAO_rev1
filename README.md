# Monitoramento de Anomalias em Tempo Real

## Descrição  
Este projeto realiza o monitoramento de anomalias utilizando um **ESP32** com o sensor **HW-123**, enviando dados para uma **API Flask** que processa os valores através de modelos de **KNN e Random Forest** e faz uma **FFT**, para transformar os dados medidos no tempo, em dados no dominio da frequência, possibilitando gerar o espectro da vibração e por fim sabermos qual tipo da falha estamos tratando. Os resultados são exibidos em um **Web Dashboard**.

## Estrutura do Projeto  

```
📂 monitoramento-anomalias
│── 📂 app                  # API Flask
│   │── 📜 __init__.py       # Inicializa a aplicação Flask
│   │── 📜 routes.py         # Rotas da API
│   │── 📜 funcoesfft.py     # Centraliza todas as funções necessárias para a Transformada de Fourrier ser aplicada
│   │── 📜 config.py         # Configurações do sistema
│── 📂 models               # Modelos treinados
│   │── 📜 knn_model.pkl    # Modelo KNN treinado
│   │── 📜 rf_model.pkl     # Modelo Random Forest treinado
│   │── 📜 knn_rf_treino.py   # Código para treinar os modelos
│── 📂 services               # Modelos treinados
│   │── 📜 armazenamento.py    # Modelo KNN treinado
│── 📂 web_dashboard        # Dashboard interativo
│   │── 📜 dashboard.py      # Código principal do dashboard
│   │── 📂 templates        # Visual Aplicação WEB
│   │   │── 📜 index.html      # Parte Visual da Aplicação WEB
│── 📂 Instance         # Dados da Aplicação Nessa Pasta
│   │── 📂 datasets        # Dados para Treinamento
│   │── 📂 raw        # Dados crus vindos do ESP e salvos em CSV e SQLITE
│   │── 📂 refined        # Dados processados SQLITE prontos para passarem pelos modelos de KNN e RF
│   │   │── 📜 criar_BD.py    # Cria o Bando de Dados Sqlite do Projeto
│── 📜 main.py              # Arquivo principal da API
│── 📜 requirements.txt     # Dependências do projeto
│── 📜 README.md            # Documentação
│── 📜 swagger.yaml            # Documentação
📂 esp32_code           # Código para ESP32
│── 📜 esp32_get_data.ino # Código do ESP32 para captura e envio de dados
```

---


## Como Executar 

### Instalar os Requirements.txt
```bash
pip install -r requirements.txt
```

## Treinamento dos Modelos  
```bash   
python API_DETECTAR_ANOMALIA/models/knn_rf_treino.py                                                                                    
```

### Criar BDlocal
```bash
python API_DETECTAR_ANOMALIA\instance\criar_BD.py
```

### Iniciar API
```bash
pip install -r API_DETECTAR_ANOMALIA/requirements.txt
python API_DETECTAR_ANOMALIA/main.py
```

### Iniciar o Dashboard  
```bash
python API_DETECTAR_ANOMALIA/web_dashboard/app_dash.py
```

## Endpoints Principais  

### GET /
```bash
Descrição: Rota principal da API.

Resposta:

API de Coleta e Predição de Anomalias
```

### POST /collect
```bash
Descrição: Armazena dados de sensores para treinamento e predição.

Requisição:

{
    "dados": [[1.2, 3.4, 5.6], [7.8, 9.0, 1.2]]
}

Resposta:

{
    "mensagem": "Dados coletados e salvos com sucesso!"
}
```

### GET /predict
```bash
Descrição: Realiza a predição das últimas amostras coletadas usando modelos KNN e Random Forest.

Resposta:

{
    "amostras_utilizadas": [[0.5, 0.2, 0.1, 1.1, -0.3, 4.2]],
    "resultado_knn": ["operacao normal"],
    "resultado_rf": ["falha tendencial"],
    "classificacao": ["falha tendencial"]
}
```

### GET /fft
```bash
Descrição: Executa a Transformada Rápida de Fourier (FFT) nos últimos dados coletados e analisa possíveis falhas com base nas frequências detectadas.

Resposta:

{
    "fft_dados": { "X": { "frequencias": [0.1, 0.2, 0.3], "espectro": [1.2, 3.4, 2.1] } },
    "falhas_detectadas": {
        "X": { "pico_frequencia": 0.2, "tipo_falha": "Desbalanceamento" }
    }
}
```

## Acessando a Documentação Swagger

A documentação interativa pode ser acessada no Swagger UI utilizando uma ferramenta como [Swagger Editor](https://editor.swagger.io/) ou configurando o Flask-Swagger.

### Testando as Rotas

Utilize ferramentas como Postman ou cURL para fazer chamadas à API:

#### Prever anomalias
```sh
curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{"dados": [[0.1, -0.2, 9.8]]}'
```

#### Coletar dados
```sh
curl -X POST "http://localhost:8000/collect" -H "Content-Type: application/json" -d '{"dados": [[0.1, -0.2, 9.8]]}'
```

#### Prever usando KNN
```sh
curl -X POST "http://localhost:8000/predict_knn" -H "Content-Type: application/json" -d '{"dados": [[0.1, -0.2, 9.8]]}'
```

# Necessidades além da API

## Código do ESP32  
O ESP32 coleta os dados do acelerômetro **MPU6050 (HW-123)** e envia para a API nos endpoints:
- `/predict_knn` → Classificação via **KNN**
- `/predict_rf` → Classificação via **Random Forest**
- `/collect` → Armazena os dados para re-treinamento

### Fluxo de Funcionamento  
1. Conecta-se ao **Wi-Fi**
2. Captura dados do **acelerômetro**
3. Envia para as **APIs**
4. Exibe os resultados no **Dashboard**

---

## Dashboard de Monitoramento  
- Exibe dois **indicadores de status**:
  - **KNN** (Verde = Normal, Vermelho = Falha)
  - **Random Forest** (Verde = Normal, Vermelho = Falha)
  - **FFT** (Tipo de Falha (Rolamento, Desbalanceamento, etc), Gráfico do Espectro da Vibração)
- Atualiza automaticamente a cada **5 segundos**

---

## Tecnologias Utilizadas  
- **Python** (Flask, Dash, Scikit-learn, Requests)
- **ESP32** (Arduino, WiFi, HTTPClient, HW-123)
- **Machine Learning** (KNN e Random Forest)
- **FFT** (Transformada de Fourrier para Análise de Vibração)

# Parte Eletrônica do Projeto Utilizando ESP32

## Lista de Componentes
 
- ESP32 - Microcontrolador principal
- HW-123 - Sensor de aceleração e giroscópio
- Jumpers (macho-macho, macho-fêmea) - Para conexões
- Bateria 9V (ou via USB)
- LM7805 - Regulador de Tensão para Manter a Alimentação da Placa estabilizada em 5V

## Conexão do ESP32 com o HW-123  

| **Pino HW-123** | **Conexão no ESP32** |
|--------------------|-------------------|
| VCC               | 3.3V               |
| GND               | GND                |
| SCL               | GPIO 22            |
| SDA               | GPIO 21            |
| XDA               | **(Deixar desconectado)** |
| XCL               | **(Deixar desconectado)** |
| AD0               | GND (Define I2C em 0x68)
| INT               | **(Opcional - Pode ser conectado a um GPIO de interrupção)** |


# Informações de contato

## Autor  
Desenvolvido por: 

Nathan Rafael Pedroso Lobato.
E-mail: nathan.lobato@outlook.com.br

André Vicente Torres Martins
E-mail: andrasno@gmail.com