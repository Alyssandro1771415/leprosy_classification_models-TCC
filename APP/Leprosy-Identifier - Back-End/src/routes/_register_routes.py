from robyn import Request, Response
import json

from .prediction_informations_data_routes import get_prediction_data
from .user_consent_routes import set_user_consent
from .save_prediction_routes import save_prediction
from .prediction_history_routes import get_prediction_history


def register_routes(server):

    @server.post("/users/consent/")
    async def _(request: Request):
        return await set_user_consent(request)

    @server.post("/prediction_data/")
    async def _(request: Request):
        return await get_prediction_data(request)

    @server.post("/predictions/save/")
    async def _(request: Request):
        return await save_prediction(request)

    @server.get("/predictions/history/:user_id")
    async def _(request: Request):
        return await get_prediction_history(request)

    @server.get("/")
    async def main(request: Request):
        return Response(
            status_code=200,
            headers={
                "X-server": "Robyn",
                "Content-Type": "application/json"
            },
            description=json.dumps({"message": "Servidor inicializado"})
        )
