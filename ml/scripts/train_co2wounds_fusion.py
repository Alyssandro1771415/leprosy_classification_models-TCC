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
from xgboost.callback import EarlyStopping
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_curve, auc, precision_recall_curve
from sklearn.inspection import permutation_importance
import matplotlib.pyplot as plt
import joblib
import sys
import shap

# ==========================
# CONFIGURAÇÕES GERAIS
# ==========================
from leprosy_ml.paths import get_ml_root

ml_root = get_ml_root()
os.chdir(ml_root)

DATASET_DIR = str(ml_root / "data" / "co2wounds_v2" / "raw" / "train_images_binary")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ==========================
# FUNÇÕES AUXILIARES
# ==========================
transform_cnn = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

resnet = models.resnet101(pretrained=True)
resnet = nn.Sequential(*list(resnet.children())[:-1])
resnet.to(DEVICE)
resnet.eval()


def extract_cnn_features(img_path):
    img = Image.open(img_path).convert('RGB')
    x = transform_cnn(img).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        feat = resnet(x).squeeze().cpu().numpy()
    return feat


def extract_glcm_features(img_path):
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
    return np.array(features)


def process_dataset(base_dir):
    features, labels = [], []
    for label_name in ["leprosy", "outros"]:
        folder = os.path.join(base_dir, label_name)
        label = 1 if label_name == "leprosy" else 0
        for filename in tqdm(os.listdir(folder), desc=f"Processando {label_name}"):
            path = os.path.join(folder, filename)
            if not filename.lower().endswith((".jpg", ".png", ".jpeg")):
                continue
            try:
                cnn_feat = extract_cnn_features(path)
                glcm_feat = extract_glcm_features(path)
                combined = np.concatenate([cnn_feat, glcm_feat])
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
    random_state=42,
    eval_metric="logloss"  # ok passar aqui
)

# Treinamento simples sem early stopping
model.fit(
    X_train_scaled, y_train,
    eval_set=[(X_train_scaled, y_train), (X_val_scaled, y_val)],
    verbose=True
)

# Recupera logloss por conjunto
evals_result = model.evals_result()
final_train_logloss = evals_result['validation_0']['logloss'][-1]
final_val_logloss = evals_result['validation_1']['logloss'][-1]

print(f"LogLoss final de Treino: {final_train_logloss:.4f}")
print(f"LogLoss final de Validação: {final_val_logloss:.4f}")

# ==========================
# AVALIAÇÃO DE MÉTRICAS COMUNS
# ==========================
train_acc = model.score(X_train_scaled, y_train)
val_acc = model.score(X_val_scaled, y_val)
test_acc = model.score(X_test_scaled, y_test)

print(f"Acurácia de Treino: {train_acc:.4f}")
print(f"Acurácia de Validação: {val_acc:.4f}")
print(f"Acurácia de Teste: {test_acc:.4f}")
print(f"LogLoss final de Treino: {final_train_logloss:.4f}")
print(f"LogLoss final de Validação: {final_val_logloss:.4f}")

# ==========================
# AVALIAÇÃO COMPLETA
# ==========================
y_pred = model.predict(X_test_scaled)
print("\n🔹 Avaliação no conjunto de teste:")
print(classification_report(y_test, y_pred, target_names=["outros", "leprosy"]))

cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["outros", "leprosy"])
disp.plot(cmap="Blues", values_format='d')
plt.title("Matriz de Confusão - Teste")
plt.savefig(str(ml_root / "artifacts" / "figures" / "matriz_confusao_fusion_model.png"), dpi=300, bbox_inches="tight")
plt.close()

joblib.dump(model, str(ml_root / "artifacts" / "models" / "co2wounds" / "modelo_xgboost_glcm_resnet101.pkl"))
joblib.dump(scaler, "scaler_features.pkl")
print("\n✅ Pipeline completo finalizado e modelo salvo!")

# ==========================
# ROC / AUC
# ==========================
y_proba = model.predict_proba(X_test_scaled)[:, 1]
fpr, tpr, _ = roc_curve(y_test, y_proba)
roc_auc = auc(fpr, tpr)

plt.figure()
plt.plot(fpr, tpr, label=f"AUC = {roc_auc:.3f}")
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend()
plt.savefig(str(ml_root / "artifacts" / "figures" / "classic_metrics_fusion_model.png"))

# ==========================
# IMPORTÂNCIA DAS FEATURES
# ==========================
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test_scaled)
shap.summary_plot(shap_values, X_test_scaled, feature_names=[f"f{i}" for i in range(X_test_scaled.shape[1])])

perm_res = permutation_importance(model, X_test_scaled, y_test, n_repeats=10, random_state=42)
importances = perm_res.importances_mean
cnn_mean = np.mean(importances[:2048])
glcm_mean = np.mean(importances[2048:])
print(f"Importância média CNN: {cnn_mean:.4f}")
print(f"Importância média GLCM: {glcm_mean:.4f}")

X_test_glcm_only = np.zeros_like(X_test_scaled)
X_test_glcm_only[:, 2048:] = X_test_scaled[:, 2048:]
X_test_cnn_only = np.zeros_like(X_test_scaled)
X_test_cnn_only[:, :2048] = X_test_scaled[:, :2048]
print("Acurácia só GLCM:", model.score(X_test_glcm_only, y_test))
print("Acurácia só CNN:", model.score(X_test_cnn_only, y_test))
