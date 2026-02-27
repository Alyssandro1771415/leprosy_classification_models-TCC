from robyn import Request, Response
from src.controllers.predict_hd import PredictImageClass
import json

async def get_prediction_data(request: Request):

    if not request.files:
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"error": "Imagem não enviada"})
        )

    image_file = list(request.files.values())[0]

    controller = PredictImageClass()
    final_datas_result = controller.get_result_prediction(
        image=image_file
    )

    return Response(
        status_code=200,
        headers={
            "Content-Type": "application/json"
        },
        description=json.dumps(final_datas_result)
    )