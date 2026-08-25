from robyn import Request, Response
import json

from src.controllers.prediction_controller import PredictionController
from src.middlewares.request_logging import log_exception


async def get_prediction_history(request: Request):

    try:
        user_id = request.path_params.get("user_id")

        if not user_id:
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=json.dumps({"error": "userId é obrigatório"})
            )

        controller = PredictionController()

        result = controller.get_user_predictions(user_id)

        return Response(
            status_code=200,
            headers={"Content-Type": "application/json"},
            description=json.dumps({
                "total": len(result),
                "predictions": result
            })
        )

    except Exception as e:
        log_exception(e, "Falha ao consultar histórico")
        return Response(
            status_code=500,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"error": "Erro interno do servidor"})
        )