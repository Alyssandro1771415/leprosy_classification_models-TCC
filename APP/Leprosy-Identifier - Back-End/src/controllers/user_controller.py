from src.services.user_service import UserService


class UserController:

    def __init__(self):
        self.user_service = UserService()

    def set_consent(self, user_id: str, email: str, name: str, allow: bool):
        return self.user_service.sync_user_data(
            user_id=user_id,
            email=email,
            name=name,
            allow=allow
        )
