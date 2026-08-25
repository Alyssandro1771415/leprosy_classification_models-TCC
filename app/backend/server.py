import json
import logging
import os

from dotenv import load_dotenv
from robyn import ALLOW_CORS, Request, Response, Robyn

from src.routes._register_routes import register_routes
from src.services.firebase_service import FirebaseService
from src.services.load_model import PreLoaderModel

from src.logging_config import configure_logging
from src.middlewares.auth_middleware import auth_middleware
from src.middlewares.request_logging import (
    finish_request_log,
    log_exception,
    start_request_log,
)

load_dotenv()
log_dir = configure_logging()
application_logger = logging.getLogger("leprosy.application")

origins = ["*"]

server = Robyn(__file__)


@server.exception
def _handle_unhandled_exception(error: Exception):
    log_exception(error, "Exceção não tratada")
    return Response(
        status_code=500,
        headers={"Content-Type": "application/json"},
        description=json.dumps({"error": "Erro interno do servidor"}),
    )


try:
    FirebaseService.initialize()
    model_preloader = PreLoaderModel()
    model_preloader.model_loader()
except Exception as error:
    log_exception(error, "Falha durante inicialização")
    raise

ALLOW_CORS(
    server,
    origins,
    headers=["Content-Type", "x-access-token"],
)


@server.before_request()
def _start_request_log(request: Request):
    return start_request_log(request)


@server.before_request()
async def _auth(request: Request):
    if request.method == "OPTIONS":
        return Response(
            status_code=200,
            headers={},
            description="OK"
        )

    return await auth_middleware(request)


@server.after_request()
def _finish_request_log(request: Request, response: Response):
    return finish_request_log(request, response)


register_routes(server)


port_str = os.getenv("PORT")

if not port_str or port_str.strip() == "":
    port = 5000
else:
    try:
        port = int(port_str)
    except ValueError:
        port = 5000

application_logger.info(
    "Servidor iniciando host=0.0.0.0 port=%s log_dir=%s",
    port,
    log_dir,
)

server.start(host="0.0.0.0", port=port)
