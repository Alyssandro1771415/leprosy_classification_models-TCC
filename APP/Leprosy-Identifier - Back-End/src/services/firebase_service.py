import firebase_admin
from firebase_admin import credentials, firestore
import os

class FirebaseService:
    _db = None

    @classmethod
    def initialize(cls):
        if not firebase_admin._apps:
            print(f"Arquivos na raiz: {os.listdir('.')}")
            if os.path.exists('src'):
                print(f"Arquivos em src: {os.listdir('src')}")

            possible_paths = [
                os.getenv("FIREBASE_CREDENTIALS"),
                "serviceAccountKey.json",
                "src/config/serviceAccountKey.json",
                "/etc/secrets/serviceAccountKey.json"
            ]

            cred_path = None
            for path in possible_paths:
                if path and os.path.exists(path):
                    cred_path = path
                    break

            if not cred_path:
                raise Exception(f"Arquivo de credenciais do Firebase não encontrado. Tentados: {possible_paths}")

            print(f"--- Firebase inicializado usando: {cred_path} ---")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        cls._db = firestore.client()

    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls.initialize()
        return cls._db