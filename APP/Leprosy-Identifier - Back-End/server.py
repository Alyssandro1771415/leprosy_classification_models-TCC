from robyn import Robyn, Request, ALLOW_CORS
from dotenv import load_dotenv
import os

from src.routes._register_routes import register_routes
from src.services.firebase_service import FirebaseService

#from src.middlewares.auth_middleware import auth_middleware

load_dotenv()

origins = os.getenv("CORS_PORT_LINK", "http://localhost")
print(origins)

server = Robyn(__file__)

FirebaseService.initialize()

ALLOW_CORS(
    server,
    [origins],
    headers=["Content-Type", "x-access-token"],
)


#@server.before_request()
#async def _auth(request: Request):
#    return await auth_middleware(request)


register_routes(server)


server.start(
    host=os.getenv("ROBYN_HOST", "0.0.0.0"),
    port=os.getenv("PORT", 5000),
    keep_alive_timeout=30,
    client_timeout=30
)
