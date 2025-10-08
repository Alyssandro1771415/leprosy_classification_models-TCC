import os
import tensorflow as tf

def save_model(model_to_save, model_name):
    """
    Salva um modelo Keras no formato oficial (.keras)
    """
    os.makedirs('models', exist_ok=True)
    model_path = f'./models/{model_name}.keras'
    model_to_save.save(model_path)
    print(f"✅ Modelo salvo em: {model_path}")

def load_model(model_path):
    """
    Carrega um modelo Keras salvo no formato oficial (.keras)
    """
    model_path = f'{model_path}.keras'
    model = tf.keras.models.load_model(model_path)
    print(f"✅ Modelo carregado de: {model_path}")
    return model
