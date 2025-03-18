import os

class Config:
    PORTA = int(os.getenv("PORTA", 8000))
    DEBUG = True
    SECRET_KEY = os.getenv("SECRET_KEY", None)  # Pode ser None sem quebrar a API
