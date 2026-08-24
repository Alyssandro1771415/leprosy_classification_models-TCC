import os

import gdown
import tf_keras as keras
from dotenv import load_dotenv

load_dotenv()


class PreLoaderModel:
    _instance = None
    _initialized = False

    model_path = "./src/model/modelo_binario_co2wounds_ablation_y_bilateral.keras"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

    def _download_model(self):
        """Baixa o modelo do Google Drive se ele não existir localmente."""
        if not os.path.exists(self.model_path):
            model_drive_id = os.getenv("MODEL_ID")

            print("\033[94mModelo não encontrado localmente. Iniciando download do Google Drive...\033[0m")

            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

            url = f"https://drive.google.com/uc?id={model_drive_id}"
            try:
                gdown.download(url, self.model_path, quiet=False)
                print("✅ Download concluído com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao baixar o modelo: {e}")
                raise e
        else:
            print("\033[92mModelo já existe localmente. Pulando download.\033[0m")

    def model_loader(self):
        if self._initialized:
            return self.model

        self._download_model()

        print("📊 Carregando modelo no TensorFlow (tf_keras)...")
        try:
            # Modelo treinado em Keras 2 (keras.src.engine.functional) — tf_keras carrega corretamente
            self.model = keras.models.load_model(self.model_path, compile=False)
            self._initialized = True
            print(
                f"\033[92mModelo carregado! input={self.model.input_shape} output={self.model.output_shape}\033[0m"
            )
            return self.model
        except Exception as e:
            print(f"\033[91mFalha ao carregar o arquivo .keras: {e}\033[0m")
            raise e
