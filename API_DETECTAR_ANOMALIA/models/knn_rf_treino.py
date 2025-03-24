import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from scipy.stats import kurtosis, skew
from scipy.fft import fft

def load_and_label_data(folder_path, labels):
    data = []
    target = []
    
    for file_name, label in labels.items():
        file_path = os.path.join(folder_path, file_name)
        try:
            df = pd.read_csv(file_path, header=0, encoding="utf-8")  # Ignorar primeira linha automaticamente
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, header=0, encoding="latin1")  # Tentar com latin1
        
        # Garantir que os dados são numéricos
        df = df.apply(pd.to_numeric, errors='coerce')
        df.dropna(inplace=True)  # Remover linhas com valores não numéricos
        
        # Criar features adicionais
        magnitude = np.sqrt(df.iloc[:, 0]**2 + df.iloc[:, 1]**2 + df.iloc[:, 2]**2)  # Magnitude do vetor de vibração
        fft_max_freq = np.array([np.max(np.abs(np.fft.fft(df.iloc[i, :], axis=0))) for i in range(df.shape[0])])  # Máxima amplitude da FFT (análise no domínio da frequência)
        mean = df.mean(axis=1)  # Média dos valores
        std = df.std(axis=1)  # Desvio padrão
        kurt = kurtosis(df, axis=1, nan_policy='omit')  # Curtose (avalia extremidades da distribuição)
        skewness = skew(df, axis=1, nan_policy='omit')  # Assimetria dos dados
        features = np.column_stack([magnitude, mean, std, kurt, skewness, fft_max_freq])
        
        data.append(features)  # Pega os valores numéricos processados
        target.extend([label] * len(df))  # Atribui o rótulo correspondente
    
    return np.vstack(data), np.array(target)

# Definição do caminho da pasta e arquivos
folder_path = "API_DETECTAR_ANOMALIA\instance\datasets" 
data_files = {
    "falha_critica.csv": "falha critica",
    "falha_tendencial.csv": "falha potencial",
    "operacao_normal.csv": "operacao normal",
    "sensor_fora.csv": "sensor fora"
}

# Carregar e rotular os dados
X, y = load_and_label_data(folder_path, data_files)

# Normalizar os dados
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Dividir os dados em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Treinar modelo KNN
knn = KNeighborsClassifier(n_neighbors=20)
knn.fit(X_train, y_train)
y_pred_knn = knn.predict(X_test)
print("Acurácia KNN:", accuracy_score(y_test, y_pred_knn))

# Treinar modelo Random Forest
rf = RandomForestClassifier(n_estimators=600, random_state=70)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
print("Acurácia Random Forest:", accuracy_score(y_test, y_pred_rf))

# Criar diretório para salvar modelos, se não existir
model_dir = "API_DETECTAR_ANOMALIA/models"
os.makedirs(model_dir, exist_ok=True)

# Salvar modelos e scaler na pasta correta
joblib.dump(knn, os.path.join(model_dir, "knn_model.pkl"))
joblib.dump(rf, os.path.join(model_dir, "rf_model.pkl"))
joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))

print("Modelos treinados e salvos com sucesso em", model_dir)