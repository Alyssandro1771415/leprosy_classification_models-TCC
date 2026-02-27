from robyn import Request, Response
import json

from src.routes.prediction_informations_data import get_prediction_data


def register_routes(server):

    @server.post("/prediction_data/")
    async def _(request: Request):
        return await get_prediction_data(request)

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
