from PIL import Image
import numpy as np
import io

class PredictImageClass:

    def get_result_prediction(self, image: bytes) -> dict:

        img_vec = self.image_to_vec(image)
        prediction = self.predict_class(img_vec)

        return {
            "prediction": float(prediction)
        }

    def image_to_vec(self, image: bytes):
        return

    def predict_class(self, img_vec):
        return
