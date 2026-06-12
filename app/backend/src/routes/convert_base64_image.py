from robyn import Request, Response
from src.controllers.image_controller import ImageController
import json

async def handle_image_upload(request: Request):
    if not request.files:
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"error": "Arquivo não encontrado"})
        )

    image_file = list(request.files.values())[0]

    controller = ImageController()

    base_64_result = controller.convert_file_to_base64(image_file)

    return Response(
        status_code=200,
        headers={"Content-Type": "application/json"},
        description=json.dumps({"base64": base_64_result})
    )