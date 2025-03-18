import os
from app import criar_app
from app.config import Config

# Inicializa a aplicação Flask usando criar_app()
app = criar_app()

if __name__ == "__main__":
    porta = Config.PORTA if hasattr(Config, "PORTA") else int(os.getenv("PORTA", 8000))
    app.run(host="0.0.0.0", port=porta, debug=Config.DEBUG)
