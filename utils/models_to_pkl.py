import os
import pickle
import keras

def save_model(model_to_save, model_name):
    os.makedirs('models', exist_ok=True)
    with open(f'./models/{model_name}.pkl', 'wb') as file:
        pickle.dump(model_to_save, file)

def load_model(model_name) -> keras.src.models.functional.Functional:
    with open(f'./models/{model_name}.pkl', 'rb') as file:
        model = pickle.load(file)
    return model
