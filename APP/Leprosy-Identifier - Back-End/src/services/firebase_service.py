import firebase_admin
from firebase_admin import credentials, firestore
import os

class FirebaseService:
    _db = None

    @classmethod
    def initialize(cls):
        if not firebase_admin._apps:
            cred_path = os.getenv("FIREBASE_CREDENTIALS")

            if not cred_path:
                raise Exception("FIREBASE_CREDENTIALS não definido no .env")

            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        cls._db = firestore.client()

    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls.initialize()
        return cls._db