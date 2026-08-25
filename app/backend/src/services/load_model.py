import logging
import os

import gdown
import tf_keras as keras
from dotenv import load_dotenv

load_dotenv()
application_logger = logging.getLogger("leprosy.application")


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
            model_drive_id = os.getenv("MODEL_ID", "").strip().strip("\"'")
            if not model_drive_id:
                raise RuntimeError("MODEL_ID não configurado")

            application_logger.info("Modelo ausente; iniciando download")

            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)

            url = f"https://drive.google.com/uc?id={model_drive_id}"
            gdown.download(url, self.model_path, quiet=False)
            application_logger.info("Download do modelo concluído path=%s", self.model_path)
        else:
            application_logger.info("Modelo encontrado localmente path=%s", self.model_path)

    def model_loader(self):
        if self._initialized:
            return self.model

        self._download_model()

        application_logger.info("Carregando modelo no TensorFlow")
        try:
            # Modelo treinado em Keras 2 (keras.src.engine.functional) — tf_keras carrega corretamente
            self.model = keras.models.load_model(self.model_path, compile=False)
            self._initialized = True
            application_logger.info(
                "Modelo carregado input=%s output=%s",
                self.model.input_shape,
                self.model.output_shape,
            )
            return self.model
        except Exception:
            application_logger.error("Falha ao carregar modelo path=%s", self.model_path)
            raise
