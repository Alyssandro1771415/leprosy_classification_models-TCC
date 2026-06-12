from src.services.firebase_service import FirebaseService
from datetime import datetime, timezone

class UserService:

    def sync_user_data(self, user_id: str, email: str, name: str = None, allow: bool = True):
        db = FirebaseService.get_db()
        user_ref = db.collection("users").document(user_id)

        now = datetime.now(timezone.utc)
        user_snapshot = user_ref.get()

        data_to_save = {
            "email": email,
            "AllowImageUsage": allow,
            "updatedAt": now
        }

        if name:
            data_to_save["name"] = name

        if not user_snapshot.exists:
            data_to_save["createdAt"] = now
            user_ref.set(data_to_save)
        else:
            user_ref.update(data_to_save)

        return {
            "userId": user_id,
            "status": "synced",
            "allowImageUsage": allow
        }