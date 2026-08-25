from robyn import Request, Response
import json

from src.controllers.user_controller import UserController
from src.middlewares.request_logging import log_exception


async def set_user_consent(request: Request):
    try:
        body_data = request.body.decode("utf-8") if isinstance(request.body, bytes) else request.body
        body = json.loads(body_data)

        user_id = body.get("user_id")
        email = body.get("email")
        name = body.get("name")
        allow = body.get("allow")

        if not user_id or allow is None:
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=json.dumps({
                    "error": "user_id e allow são obrigatórios",
                    "received": body
                })
            )

        controller = UserController()

        result = controller.set_consent(
            user_id=user_id,
            email=email,
            name=name,
            allow=allow
        )

        return Response(
            status_code=200,
            headers={"Content-Type": "application/json"},
            description=json.dumps({
                "message": "Consentimento atualizado com sucesso",
                "data": result
            })
        )

    except Exception as e:
        log_exception(e, "Falha ao atualizar consentimento")
        return Response(
            status_code=500,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"error": "Erro interno do servidor"})
        )