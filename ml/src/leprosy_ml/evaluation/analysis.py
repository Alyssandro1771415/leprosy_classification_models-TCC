import os
import pickle

import matplotlib.pyplot as plt
import numpy as np

from leprosy_ml.models.io import load_model
from leprosy_ml.paths import models_dir

def load_model_with_history(model_name):
    """
    Carrega um modelo junto com seu histórico de treinamento e informações do dataset
    
    Args:
        model_name (str): Nome do modelo (sem extensão .pkl)
    
    Returns:
        tuple: (modelo, histórico, informações_dataset)
    """
    # Carrega o modelo
    model = load_model(model_name)
    
    def _artifact_path(suffix: str) -> str:
        for dataset in ("co2wounds", "atlas"):
            path = models_dir(dataset) / f"{model_name}_{suffix}.pkl"
            if path.is_file():
                return str(path)
        legacy = f"./models/{model_name}_{suffix}.pkl"
        return legacy

    history_path = _artifact_path("history")
    history = None
    if os.path.exists(history_path):
        with open(history_path, "rb") as f:
            history = pickle.load(f)
    else:
        print(f"⚠️ Histórico não encontrado em: {history_path}")

    info_path = _artifact_path("info")
    dataset_info = None
    if os.path.exists(info_path):
        with open(info_path, 'rb') as f:
            dataset_info = pickle.load(f)
    else:
        print(f"⚠️ Informações do dataset não encontradas em: {info_path}")
    
    return model, history, dataset_info

def plot_training_history(history, model_name="Modelo"):
    """
    Plota o histórico de treinamento (acurácia e loss)
    
    Args:
        history (dict): Histórico de treinamento
        model_name (str): Nome do modelo para o título
    """
    if history is None:
        print("❌ Histórico não disponível para plotagem")
        return
    
    # Verifica se é modelo binário ou multiclasse
    has_val = 'val_accuracy' in history
    
    if has_val:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Plot da acurácia
        ax1.plot(history['accuracy'], label='Acurácia de Treinamento', color='blue')
        ax1.plot(history['val_accuracy'], label='Acurácia de Validação', color='orange')
        ax1.set_title(f'{model_name} - Evolução da Acurácia')
        ax1.set_xlabel('Épocas')
        ax1.set_ylabel('Acurácia')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot da loss
        ax2.plot(history['loss'], label='Loss de Treinamento', color='blue')
        ax2.plot(history['val_loss'], label='Loss de Validação', color='orange')
        ax2.set_title(f'{model_name} - Evolução da Loss')
        ax2.set_xlabel('Épocas')
        ax2.set_ylabel('Loss')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
    else:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        
        # Plot da acurácia
        ax1.plot(history['accuracy'], label='Acurácia de Treinamento', color='blue')
        ax1.set_title(f'{model_name} - Evolução da Acurácia')
        ax1.set_xlabel('Épocas')
        ax1.set_ylabel('Acurácia')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot da loss
        ax2.plot(history['loss'], label='Loss de Treinamento', color='blue')
        ax2.set_title(f'{model_name} - Evolução da Loss')
        ax2.set_xlabel('Épocas')
        ax2.set_ylabel('Loss')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def print_model_summary(model, history, dataset_info, model_name="Modelo"):
    """
    Imprime um resumo completo do modelo
    
    Args:
        model: Modelo Keras
        history (dict): Histórico de treinamento
        dataset_info (dict): Informações do dataset
        model_name (str): Nome do modelo
    """
    print(f"\n{'='*60}")
    print(f"📊 RESUMO DO MODELO: {model_name}")
    print(f"{'='*60}")
    
    # Informações do dataset
    if dataset_info:
        print(f"\n🗂️ DATASET:")
        print(f"   Total de imagens: {dataset_info['total_images']}")
        print(f"   Imagens de treino: {dataset_info['train_images']}")
        print(f"   Imagens de validação: {dataset_info['val_images']}")
        print(f"   Número de classes: {dataset_info['num_classes']}")
        print(f"   Shape de entrada: {dataset_info['input_shape']}")
        print(f"   Classes: {dataset_info['class_names']}")
        print(f"   Distribuição: {dataset_info['class_distribution']}")
    
    # Informações do modelo
    print(f"\n🧠 ARQUITETURA:")
    print(f"   Total de parâmetros: {model.count_params():,}")
    print(f"   Camadas: {len(model.layers)}")
    
    # Métricas finais
    if history:
        print(f"\n📈 MÉTRICAS FINAIS:")
        final_acc = history['accuracy'][-1]
        final_loss = history['loss'][-1]
        print(f"   Acurácia final (treino): {final_acc:.4f} ({final_acc*100:.2f}%)")
        print(f"   Loss final (treino): {final_loss:.4f}")
        
        if 'val_accuracy' in history:
            final_val_acc = history['val_accuracy'][-1]
            final_val_loss = history['val_loss'][-1]
            print(f"   Acurácia final (validação): {final_val_acc:.4f} ({final_val_acc*100:.2f}%)")
            print(f"   Loss final (validação): {final_val_loss:.4f}")
            
            # Análise de overfitting
            acc_diff = final_acc - final_val_acc
            if acc_diff > 0.1:
                print(f"   ⚠️ Possível overfitting (diferença de acurácia: {acc_diff:.4f})")
            else:
                print(f"   ✅ Modelo bem generalizado (diferença de acurácia: {acc_diff:.4f})")
        
        print(f"   Épocas treinadas: {len(history['accuracy'])}")
    
    print(f"\n{'='*60}")

def analyze_model(model_name):
    """
    Função completa para analisar um modelo salvo
    
    Args:
        model_name (str): Nome do modelo (sem extensão .pkl)
    """
    print(f"🔍 Carregando e analisando modelo: {model_name}")
    
    try:
        model, history, dataset_info = load_model_with_history(model_name)
        
        # Imprime resumo
        print_model_summary(model, history, dataset_info, model_name)
        
        # Plota histórico
        if history:
            plot_training_history(history, model_name)
        
        return model, history, dataset_info
        
    except Exception as e:
        print(f"❌ Erro ao analisar modelo: {e}")
        return None, None, None
