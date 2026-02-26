from robyn import Robyn, Request, ALLOW_CORS
from dotenv import load_dotenv
import os

from src.middlewares.auth_middleware import auth_middleware
from src.routes._register_routes import register_routes

load_dotenv()

server = Robyn(__file__)
ALLOW_CORS(server,
            [os.getenv("CORS_PORT_LINK")],
            headers=["Content-Type", "x-access-token"]
        )


@server.before_request()
async def _auth(request: Request):
    return await auth_middleware(request)


register_routes(server)


server.start(
    host=os.getenv("ROBYN_HOST"),
    port=os.getenv("ROBYN_PORT"),
    keep_alive_timeout=30,
    client_timeout=30
)
