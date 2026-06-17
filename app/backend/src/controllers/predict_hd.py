import numpy as np

from src.services.load_model import PreLoaderModel
from src.services.preprocessing_service import prepare_model_input_dict


class PredictImageClass:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        model_pre_loader = PreLoaderModel()
        self.model = model_pre_loader.model_loader()

    def get_result_prediction(self, image: bytes) -> dict:

        img_vec = self.prepare_image_vector(image)
        probability = self.predict_class(img_vec)

        predicted_class = "outro" if probability <= 0.5 else "leprosy"

        return {
            "predicted_class": predicted_class,
            "probability": round(probability, 4)
        }

    def prepare_image_vector(self, image: bytes):
        return prepare_model_input_dict(image)

    def predict_class(self, img_vec):
        prediction = self.model.predict(img_vec, verbose=0)

        return float(prediction[0][0])
