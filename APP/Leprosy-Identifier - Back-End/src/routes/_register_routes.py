from robyn import Request, Response
import json


from src.routes.prediction_informations_data import get_predction_data



def register_routes(server):

    @server.get("/birth_informations_data/:image")
    async def _(request: Request):
        return await get_predction_data(request)

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
