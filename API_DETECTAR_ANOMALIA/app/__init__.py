from flask import Flask
from flask_cors import CORS
from app.routes import configurar_rotas

def criar_app():
    app = Flask(__name__)
    CORS(app)
    configurar_rotas(app)
    return app