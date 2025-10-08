import torch
import torch.nn.functional as F
from torchvision import models, transforms
import cv2
import numpy as np
from PIL import Image

# -------------------
# Modelo
# -------------------
# Usar a forma nova de carregar pesos
from torchvision.models import ResNet50_Weights
model = models.resnet50(weights=ResNet50_Weights.DEFAULT)
model.eval()

# -------------------
# Imagem
# -------------------
img_path = "/home/alyssandro/Documents/Github/leprosy_classification_models-TCC/data/CO2Wounds-V2/raw/train_images_binary/train/outros/imagem_58.jpg"
img = Image.open(img_path).convert("RGB")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])
input_tensor = transform(img).unsqueeze(0)

# -------------------
# Hooks para Grad-CAM
# -------------------
gradients = []
activations = []

def forward_hook(module, input, output):
    activations.append(output.detach())

def backward_hook(module, grad_input, grad_output):
    gradients.append(grad_output[0].detach())

# Pegar o último bloco convolucional
target_layer = model.layer4[-1]
target_layer.register_forward_hook(forward_hook)
target_layer.register_full_backward_hook(backward_hook)

# -------------------
# Forward + Backward
# -------------------
output = model(input_tensor)
pred_class = output.argmax(dim=1).item()

model.zero_grad()
output[0, pred_class].backward()

# -------------------
# Construção do CAM
# -------------------
# grads: média global em cada canal
grads = gradients[0].mean(dim=[0, 2, 3])   
# ativação da camada
acts = activations[0][0]                    

# Combinar pesos (grads) com ativação
cam = torch.zeros(acts.shape[1:], dtype=torch.float32)
for i, w in enumerate(grads):
    cam += w * acts[i, :, :]

# Normalizar para [0,1]
cam = torch.clamp(cam, min=0).numpy()
cam = cv2.resize(cam, (224, 224))
cam = (cam - cam.min()) / (cam.max() - cam.min())

# -------------------
# Visualização
# -------------------
heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
img_np = np.array(img.resize((224, 224)))
result = cv2.addWeighted(img_np, 0.5, heatmap, 0.5, 0)

cv2.imwrite("gradcam_result.jpg", result)

print(f"Classe prevista: {pred_class}, resultado salvo em gradcam_result.jpg")
