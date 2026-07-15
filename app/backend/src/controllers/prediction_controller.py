from src.services.prediction_service import PredictionService


class PredictionController:

    def __init__(self):
        self.prediction_service = PredictionService()

    def save_prediction(
        self,
        user_id: str,
        image_base64: str,
        prediction: str,
        confidence: float,
        model_version: str,
        allow_for_training: str
    ):
        return self.prediction_service.save_prediction(
            user_id,
            image_base64,
            prediction,
            confidence,
            model_version,
            allow_for_training
        )

    def get_user_predictions(self, user_id: str):
        result = self.prediction_service.get_user_predictions(user_id)
        return result

    def delete_prediction(self, user_id: str, prediction_id: str):
        return self.prediction_service.delete_prediction(user_id, prediction_id)
