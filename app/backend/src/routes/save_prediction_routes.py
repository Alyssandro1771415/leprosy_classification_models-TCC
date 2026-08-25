from robyn import Request, Response
import json

from src.controllers.prediction_controller import PredictionController
from src.middlewares.request_logging import log_exception


async def save_prediction(request: Request):

    try:
        body_data = request.body.decode("utf-8") if isinstance(request.body, bytes) else request.body
        body = json.loads(body_data)

        user_id = body.get("user_id")
        image_base64 = body.get("image_base64")
        prediction = body.get("prediction")
        confidence = body.get("confidence")
        model_version = body.get("model_version") or body.get("modelVersion")
        allow_for_training = body.get("allow_for_training")

        if not user_id or not image_base64:
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=json.dumps({
                    "error": "userId e imageBase64 são obrigatórios"
                })
            )

        controller = PredictionController()

        result = controller.save_prediction(
            user_id=user_id,
            image_base64=image_base64,
            prediction=prediction,
            confidence=confidence,
            model_version=model_version,
            allow_for_training=allow_for_training
        )

        return Response(
            status_code=200,
            headers={"Content-Type": "application/json"},
            description=json.dumps({
                "message": "Predição salva com sucesso",
                "data": result
            })
        )

    except Exception as e:
        log_exception(e, "Falha ao salvar predição")
        return Response(
            status_code=500,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"error": "Erro interno do servidor"})
        )