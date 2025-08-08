import os
import pickle

def save_model(model_to_save, model_name):
    """
    Salva um modelo Keras usando pickle
    """
    os.makedirs('models', exist_ok=True)
    with open(f'./models/{model_name}.pkl', 'wb') as file:
        pickle.dump(model_to_save, file)
    print(f"Modelo salvo em: ./models/{model_name}.pkl")

def load_model(model_name):
    """
    Carrega um modelo Keras salvo com pickle
    """
    with open(f'./models/{model_name}.pkl', 'rb') as file:
        model = pickle.load(file)
    return model
