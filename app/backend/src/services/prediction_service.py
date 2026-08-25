from src.services.firebase_service import FirebaseService
from src.services.image_service import ImageService
from datetime import datetime, timezone
import uuid

from google.cloud.firestore_v1.base_document import DocumentSnapshot


class PredictionService:

    def __init__(self):
            self.db = FirebaseService.get_db()

    def save_prediction(
        self,
        user_id: str,
        image_base64: str,
        prediction: str,
        confidence: float,
        model_version: str,
        allow_for_training: bool,
    ):
        db = FirebaseService.get_db()

        user_ref = db.collection("users").document(user_id)

        user_doc = user_ref.get()

        if not user_doc.exists:
            now = datetime.now(timezone.utc)
            user_ref.set({
                "email": "",
                "AllowImageUsage": False,
                "createdAt": now,
                "updatedAt": now,
            })

        prediction_id = str(uuid.uuid4())

        image_service = ImageService()
        stored_image_base64 = image_service.compress_base64_for_storage(image_base64)

        prediction_data = {
            "imageBase64": stored_image_base64,
            "prediction": prediction,
            "confidence": confidence,
            "createdAt": datetime.now(),
            "modelVersion": model_version,
            "allowForTraining": allow_for_training
        }

        user_ref.collection("predictions").document(prediction_id).set(prediction_data)

        return {
            "predictionId": prediction_id,
            "allowForTraining": allow_for_training
        }

    def get_user_predictions(self, user_id: str):
            try:
                docs = self.db.collection("users").document(user_id).collection("predictions").get()

                predictions = []
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id

                    img_data = data.get('image_base64')
                    if isinstance(img_data, bytes):
                        data['image_base64'] = img_data.decode('utf-8')

                    created_at = data.get('createdAt')
                    if created_at and hasattr(created_at, 'isoformat'):
                        data['createdAt'] = created_at.isoformat()

                    predictions.append(data)

                return predictions
            except Exception:
                raise

    def delete_prediction(self, user_id: str, prediction_id: str):
        user_ref = self.db.collection("users").document(user_id)
        prediction_ref = user_ref.collection("predictions").document(prediction_id)

        if not prediction_ref.get().exists:
            raise Exception("Análise não encontrada")

        prediction_ref.delete()

        return {
            "deleted": True,
            "predictionId": prediction_id,
        }
