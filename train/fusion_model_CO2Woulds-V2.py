import os
import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from skimage.feature import graycomatrix, graycoprops
from skimage.color import rgb2gray
from tqdm import tqdm
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import sys

# ==========================
# CONFIGURAÇÕES GERAIS
# ==========================

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

DATASET_DIR = "data/CO2Wounds-V2/raw/train_images_binary"  # ajuste se necessário
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ==========================
# FUNÇÕES AUXILIARES
# ==========================

# Transformação padrão para a CNN
transform_cnn = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# Carregar modelo ResNet101 sem a última camada (extrator de features)
resnet = models.resnet101(pretrained=True)
resnet = nn.Sequential(*list(resnet.children())[:-1])  # remove camada FC
resnet.to(DEVICE)
resnet.eval()


def extract_cnn_features(img_path):
    """Extrai as features profundas da ResNet101."""
    img = Image.open(img_path).convert('RGB')
    x = transform_cnn(img).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        feat = resnet(x).squeeze().cpu().numpy()

    return feat  # vetor 2048D


def extract_glcm_features(img_path):
    """Extrai features de textura (GLCM)."""
    img = Image.open(img_path).convert('RGB')
    img_gray = rgb2gray(np.array(img))
    img_gray = (img_gray * 255).astype('uint8')

    glcm = graycomatrix(img_gray, [1], [0], symmetric=True, normed=True)
    features = [
        graycoprops(glcm, 'contrast')[0, 0],
        graycoprops(glcm, 'homogeneity')[0, 0],
        graycoprops(glcm, 'energy')[0, 0],
        graycoprops(glcm, 'correlation')[0, 0],
    ]
    return np.array(features)  # vetor 4D


def process_dataset(base_dir):
    """Percorre todas as imagens em X/ e outros/, retornando vetores e rótulos."""
    features, labels = [], []

    for label_name in ["leprosy", "outros"]:
        folder = os.path.join(base_dir, label_name)
        label = 1 if label_name == "leprosy" else 0

        for filename in tqdm(os.listdir(folder), desc=f"Processando {label_name} em {base_dir}"):
            path = os.path.join(folder, filename)
            if not filename.lower().endswith((".jpg", ".png", ".jpeg")):
                continue

            try:
                cnn_feat = extract_cnn_features(path)
                glcm_feat = extract_glcm_features(path)
                combined = np.concatenate([cnn_feat, glcm_feat])  # vetor final
                features.append(combined)
                labels.append(label)
            except Exception as e:
                print(f"Erro em {path}: {e}")

    return np.array(features), np.array(labels)


# ==========================
# EXTRAÇÃO DE FEATURES
# ==========================

print("🔹 Extraindo features do conjunto de treino...")
X_train, y_train = process_dataset(os.path.join(DATASET_DIR, "train"))

print("🔹 Extraindo features do conjunto de validação...")
X_val, y_val = process_dataset(os.path.join(DATASET_DIR, "val"))

print("🔹 Extraindo features do conjunto de teste...")
X_test, y_test = process_dataset(os.path.join(DATASET_DIR, "test"))

# ==========================
# PRÉ-PROCESSAMENTO
# ==========================

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

# ==========================
# TREINAMENTO DO MODELO FINAL (XGBoost)
# ==========================

print("🔹 Treinando modelo XGBoost com features combinadas...")
model = xgb.XGBClassifier(
    n_estimators=400,
    learning_rate=0.03,
    max_depth=8,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)
model.fit(X_train_scaled, y_train, eval_set=[(X_val_scaled, y_val)], verbose=True)

# ==========================
# AVALIAÇÃO
# ==========================

y_pred = model.predict(X_test_scaled)
print("\n🔹 Avaliação no conjunto de teste:")
print(classification_report(y_test, y_pred, target_names=["outros", "leprosy"]))
print("Matriz de confusão:\n", confusion_matrix(y_test, y_pred))

# ==========================
# SALVAR MODELO E ESCALER
# ==========================

joblib.dump(model, "modelo_xgboost_glcm_resnet101.pkl")
joblib.dump(scaler, "scaler_features.pkl")

print("\n✅ Pipeline completo finalizado e modelo salvo!")
