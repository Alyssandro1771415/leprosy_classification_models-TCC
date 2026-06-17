import tensorflow as tf
import os
import gdown

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


            print("🚚 Modelo não encontrado localmente. Iniciando download do Google Drive...")

            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

            url = f'https://drive.google.com/uc?id={model_drive_id}'
            try:
                gdown.download(url, self.model_path, quiet=False)
                print("✅ Download concluído com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao baixar o modelo: {e}")
                raise e
        else:
            print("📂 Modelo já existe localmente. Pulando download.")

    def model_loader(self):
        if self._initialized:
            return self.model

        self._download_model()

        print("📊 Carregando modelo no TensorFlow...")
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            self._initialized = True
            print(f"✅ Modelo carregado na memória!")
            return self.model
        except Exception as e:
            print(f"❌ Falha ao carregar o arquivo .keras: {e}")
            raise e