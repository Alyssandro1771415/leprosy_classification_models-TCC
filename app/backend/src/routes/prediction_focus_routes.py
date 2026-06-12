from robyn import Request, Response
import json

from src.controllers.model_focus_controller import ModelFocusController


async def get_prediction_focus(request: Request):
    if not request.files:
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"error": "Imagem não enviada"})
        )

    image_file = list(request.files.values())[0]

    controller = ModelFocusController()
    focus_result = controller.get_model_focus(image=image_file)

    return Response(
        status_code=200,
        headers={"Content-Type": "application/json"},
        description=json.dumps(focus_result)
    )
