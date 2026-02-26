from robyn import Request, Response
from src.controllers.predict_hd import PredictImageClass
import json

async def get_prediction_data(request: Request):

    if "image" not in request.files:
        return Response(
            status_code=400,
            description=json.dumps({"error": "Imagem não enviada"})
        )

    image_file = request.files["image"]

    image_bytes = image_file["content"]

    controller = PredictImageClass()
    final_datas_result = controller.get_result_prediction(
        image=image_bytes
    )

    return Response(
        status_code=200,
        headers={
            "Content-Type": "application/json"
        },
        description=json.dumps(final_datas_result)
    )