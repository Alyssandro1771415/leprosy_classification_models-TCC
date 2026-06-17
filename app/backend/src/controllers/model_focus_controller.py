from src.services.load_model import PreLoaderModel
from src.services.model_focus_service import ModelFocusService


class ModelFocusController:
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
        model = model_pre_loader.model_loader()
        self.model_focus_service = ModelFocusService(model)
        self._initialized = True

    def get_model_focus(self, image: bytes) -> dict:
        return self.model_focus_service.generate_focus_result(image)
