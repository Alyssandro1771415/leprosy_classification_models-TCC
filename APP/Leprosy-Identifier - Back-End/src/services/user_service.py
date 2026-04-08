from src.services.firebase_service import FirebaseService
from datetime import datetime, timezone

class UserService:

    def set_user_consent(self, user_id: str, email: str, allow: bool):
        db = FirebaseService.get_db()
        user_ref = db.collection("users").document(user_id)

        now = datetime.now(timezone.utc)

        user_snapshot = user_ref.get()

        if user_snapshot.exists:
            user_ref.update({
                "email": email,
                "AllowImageUsage": allow,
                "updatedAt": now
            })
        else:
            user_ref.set({
                "AllowImageUsage": allow,
                "createdAt": now,
                "updatedAt": now
            })

        return {
            "userId": user_id,
            "allowImageUsage": allow
        }