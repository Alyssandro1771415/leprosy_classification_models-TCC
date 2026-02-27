from robyn import Request, Response
import json

from src.controllers.user_controller import UserController


async def set_user_consent(request: Request):

    try:
        body = json.loads(request.body)

        user_id = body.get("userId")
        email = body.get("email")
        allow = body.get("allowImageUsage")

        if not user_id or allow is None:
            return Response(
                status_code=400,
                headers={"Content-Type": "application/json"},
                description=json.dumps({
                    "error": "userId e allowImageUsage são obrigatórios"
                })
            )

        controller = UserController()

        result = controller.set_consent(
            user_id=user_id,
            email=email,
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
        return Response(
            status_code=500,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"error": str(e)})
        )