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


port_str = os.getenv("PORT")

if not port_str or port_str.strip() == "":
    port = 5000
else:
    try:
        port = int(port_str)
    except ValueError:
        port = 5000

print(f"--- Iniciando servidor na porta: {port} ---")

server.start(host="0.0.0.0", port=port)