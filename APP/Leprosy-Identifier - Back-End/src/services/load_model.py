import tensorflow as tf

class PreLoaderModel:
    _instance = None
    _initialized = False

    model_path = "./src/model/modelo_binario_co2wounds.keras"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

    def model_loader(self):
        if self._initialized:
            return self.model

        print("📊 Carregando moodelo...")
        self.model = tf.keras.models.load_model(self.model_path)

        self._initialized = True
        print(f"✅ Modelo carregado!")
        return self.model
