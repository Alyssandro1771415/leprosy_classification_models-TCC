from src.services.firebase_service import FirebaseService
from datetime import datetime
import uuid

from google.cloud.firestore_v1.base_document import DocumentSnapshot


class PredictionService:

    def save_prediction(
        self,
        user_id: str,
        image_base64: str,
        prediction: str,
        confidence: float,
        model_version: str
    ):
        db = FirebaseService.get_db()

        user_ref = db.collection("users").document(user_id)

        user_doc = user_ref.get()

        if not user_doc.exists:
            raise Exception("Usuário não encontrado")

        user_data = user_doc.to_dict()

        allow_for_training = user_data.get("allowImageUsage", False)

        prediction_id = str(uuid.uuid4())

        prediction_data = {
            "imageBase64": image_base64,
            "prediction": prediction,
            "confidence": confidence,
            "createdAt": datetime.utcnow(),
            "modelVersion": model_version,
            "allowForTraining": allow_for_training
        }

        user_ref.collection("predictions").document(prediction_id).set(prediction_data)

        return {
            "predictionId": prediction_id,
            "allowForTraining": allow_for_training
        }

    def get_user_predictions(self, user_id: str):
        db = FirebaseService.get_db()

        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise Exception("Usuário não encontrado")

        predictions_ref = user_ref.collection("predictions") \
            .order_by("createdAt", direction="DESCENDING")

        predictions = predictions_ref.stream()

        results = []

        for doc in predictions:
            data = doc.to_dict()

            # 🔥 Converter datetime para string ISO
            if "createdAt" in data and data["createdAt"]:
                data["createdAt"] = data["createdAt"].isoformat()

            data["predictionId"] = doc.id

            results.append(data)

        return results