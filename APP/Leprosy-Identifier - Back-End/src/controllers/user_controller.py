from src.services.user_service import UserService


class UserController:

    def __init__(self):
        self.user_service = UserService()

    def set_consent(self, user_id: str, email: str, allow: bool):
        return self.user_service.set_user_consent(
            user_id=user_id,
            email=email,
            allow=allow
        )
