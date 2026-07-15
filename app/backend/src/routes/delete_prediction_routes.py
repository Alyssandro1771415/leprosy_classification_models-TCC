from robyn import Request, Response
import json

from src.controllers.prediction_controller import PredictionController


async def delete_prediction(request: Request):
    try:
        user_id = request.path_params.get("user_id")
        prediction_id = request.path_params.get("prediction_id")

        if not user_id or not prediction_id:
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=json.dumps({"error": "userId e predictionId são obrigatórios"}),
            )

        controller = PredictionController()
        result = controller.delete_prediction(user_id, prediction_id)

        return Response(
            status_code=200,
            headers={"Content-Type": "application/json"},
            description=json.dumps(result),
        )

    except Exception as e:
        status_code = 404 if "não encontrada" in str(e).lower() else 500
        return Response(
            status_code=status_code,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"error": str(e)}),
        )
