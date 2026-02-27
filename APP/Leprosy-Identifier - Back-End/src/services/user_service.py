from src.services.firebase_service import FirebaseService
from datetime import datetime


class UserService:

    def set_user_consent(self, user_id: str, email: str, allow: bool):
        db = FirebaseService.get_db()

        user_ref = db.collection("users").document(user_id)

        user_data = {
            "email": email,
            "allowImageUsage": allow,
            "updatedAt": datetime.utcnow()
        }

        if not user_ref.get().exists:
            user_data["createdAt"] = datetime.utcnow()

        user_ref.set(user_data, merge=True)

        return {
            "userId": user_id,
            "allowImageUsage": allow
        }