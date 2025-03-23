#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>

// Configuração da rede Wi-Fi
const char* WIFI_SSID = "SEU_WIFI_AQUI";
const char* WIFI_PASS = "SUA_SENHA_AQUI";

// URLs da API
const char* SERVER_URL_PREDICT = "http://192.168.0.XXX:8000/predict"; // Troque o XXX pelo IP do seu servidor
const char* SERVER_URL_COLLECT = "http://192.168.0.XXX:8000/collect"; // Troque o XXX pelo IP do seu servidor

// Endereço I2C do HW-123
const int HW123_ADDR = 0x68;

// Tempo de envio (a cada X milissegundos)
const int INTERVALO_ENVIO = 5000;
unsigned long ultimoEnvio = 0;

void setup() {
    Serial.begin(115200);
    WiFi.begin(WIFI_SSID, WIFI_PASS);

    Serial.print("Conectando ao Wi-Fi...");
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(1000);
    }
    Serial.println("\nWi-Fi conectado!");

    // Inicializa o HW-123
    Wire.begin();
    Wire.beginTransmission(HW123_ADDR);
    Wire.write(0x6B);  // Registrador de energia
    Wire.write(0);     // Liga o sensor
    Wire.endTransmission();
    Serial.println("HW-123 iniciado com sucesso!");
}

void loop() {
    if (millis() - ultimoEnvio > INTERVALO_ENVIO) {
        ultimoEnvio = millis();

        // Captura os dados do sensor
        float accX1, accY1, accZ1;
        float accX2, accY2, accZ2;
        lerAcelerometro(&accX1, &accY1, &accZ1);  // Leitura da 1ª amostra
        lerAcelerometro(&accX2, &accY2, &accZ2);  // Leitura da 2ª amostra

        // Cria o JSON no formato 2D
        String jsonData = "{\"dados\": [[";
        jsonData += String(accX1) + "," + String(accY1) + "," + String(accZ1) + "],";
        jsonData += "[" + String(accX2) + "," + String(accY2) + "," + String(accZ2) + "]";
        jsonData += "]}";

        // Consultar API de predição usando GET
        if (consultarPredict(SERVER_URL_PREDICT)) {
            Serial.println("Consulta ao /predict realizada com sucesso!");
        } else {
            Serial.println("Erro ao consultar /predict.");
        }

        // Enviar para API de armazenamento (/collect)
        if (enviarParaAPI(SERVER_URL_COLLECT, jsonData)) {
            Serial.println("Dados enviados para /collect com sucesso!");
        } else {
            Serial.println("Erro ao enviar para /collect.");
        }
    }

    // Reconectar Wi-Fi se necessário
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Wi-Fi desconectado! Reconectando...");
        WiFi.begin(WIFI_SSID, WIFI_PASS);
    }
}

// Função para ler os dados do acelerômetro HW-123
void lerAcelerometro(float* x, float* y, float* z) {
    Wire.beginTransmission(HW123_ADDR);
    Wire.write(0x3B);  // Registrador do eixo X
    Wire.endTransmission(false);
    Wire.requestFrom(HW123_ADDR, 6, true);

    int16_t rawX = (Wire.read() << 8) | Wire.read();
    int16_t rawY = (Wire.read() << 8) | Wire.read();
    int16_t rawZ = (Wire.read() << 8) | Wire.read();

    *x = rawX / 16384.0; // Conversão para g
    *y = rawY / 16384.0;
    *z = rawZ / 16384.0;
}

// Função para enviar os dados para a API (POST)
bool enviarParaAPI(const char* url, String jsonPayload) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Wi-Fi desconectado!");
        return false;
    }

    HTTPClient http;
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode < 0) {
        Serial.println("Falha ao conectar ao servidor.");
        Serial.print("Erro: ");
        Serial.println(http.errorToString(httpResponseCode).c_str());
        http.end();
        return false;
    }

    String response = http.getString();
    Serial.print("Resposta da API [");
    Serial.print(httpResponseCode);
    Serial.println("]: ");
    Serial.println(response);

    http.end();
    return (httpResponseCode == 200 || httpResponseCode == 201);
}

// Função para consultar a API de predição (GET) e exibir o resultado no console
bool consultarPredict(const char* url) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("Wi-Fi desconectado!");
        return false;
    }

    HTTPClient http;
    http.begin(url);

    int httpResponseCode = http.GET();

    if (httpResponseCode < 0) {
        Serial.println("Falha ao conectar ao servidor.");
        Serial.print("Erro: ");
        Serial.println(http.errorToString(httpResponseCode).c_str());
        http.end();
        return false;
    }

    // Exibe o código de resposta e o corpo da resposta no console
    String response = http.getString();
    Serial.print("Resposta da API [");
    Serial.print(httpResponseCode);
    Serial.println("]: ");
    Serial.println("Resultado do GET:");
    Serial.println(response);

    http.end();
    return (httpResponseCode == 200 || httpResponseCode == 201);
}
