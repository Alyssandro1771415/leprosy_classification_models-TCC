import json
import logging
import os

from dotenv import load_dotenv
from robyn import Request, Response

load_dotenv()
application_logger = logging.getLogger("leprosy.application")

SECRET_TOKEN = os.getenv("SECRET_TOKEN")

EXCLUDED_ROUTES = ["/"]

async def auth_middleware(request: Request):
    if request is None:
        return

    path = request.url.path

    if request.method == "OPTIONS":
        return request

    if path in EXCLUDED_ROUTES:
        return request

    if not SECRET_TOKEN:
        application_logger.error("SECRET_TOKEN não configurado")
        return Response(
            status_code=500,
            headers={"Content-Type": "application/json"},
            description=json.dumps({
                "error": "Configuração de autenticação não encontrada"
            })
        )

    token = request.headers.get("X-Access-Token")

    if not token:
        return Response(
            status_code=401,
            headers={"Content-Type": "application/json"},
            description=json.dumps({
                "error": "Token de acesso não fornecido. Use o header X-Access-Token"
            })
        )

    if token != SECRET_TOKEN:
        return Response(
            status_code=401,
            headers={"Content-Type": "application/json"},
            description=json.dumps({
                "error": "Não autorizado"
            })
        )

    return request
