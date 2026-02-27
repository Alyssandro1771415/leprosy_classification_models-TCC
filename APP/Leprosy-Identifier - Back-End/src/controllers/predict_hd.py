from PIL import Image
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
import numpy as np
import io

from src.services.load_model import PreLoaderModel


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

        predicted_class = "leprosy" if probability <= 0.5 else "outro"

        return {
            "predicted_class": predicted_class,
            "probability": round(probability, 4)
        }

    def prepare_image_vector(self, image: bytes):
       original_image = Image.open(io.BytesIO(image))
       original_image = original_image.convert("RGB")
       original_image = original_image.resize((224, 224))

       img_array = np.array(original_image)
       img_array = np.expand_dims(img_array, axis=0)

       img_array = preprocess_input(img_array)

       return img_array

    def predict_class(self, img_vec):
        prediction = self.model.predict(img_vec)
        return float(prediction[0][0])
