import logging
import os

import firebase_admin
from firebase_admin import credentials, firestore

application_logger = logging.getLogger("leprosy.application")

class FirebaseService:
    _db = None

    @classmethod
    def initialize(cls):
        if not firebase_admin._apps:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.abspath(os.path.join(current_dir, "../../"))

            possible_paths = [
                os.path.join(root_dir, "serviceAccountKey.json"),
                os.path.join(root_dir, "src/config/serviceAccountKey.json"),
                "/etc/secrets/serviceAccountKey.json",
                "serviceAccountKey.json"
            ]

            cred_path = None
            for path in possible_paths:
                if path and os.path.exists(path):
                    cred_path = path
                    break

            if not cred_path:
                raise Exception(f"Arquivo de credenciais do Firebase não encontrado. Tentados: {possible_paths}")

            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            application_logger.info("Firebase inicializado credential_source=%s", cred_path)

        cls._db = firestore.client()

    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls.initialize()
        return cls._db