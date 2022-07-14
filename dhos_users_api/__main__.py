import os

from waitress import serve

from .app import create_app

SERVER_PORT = os.getenv("SERVER_PORT", 5000)

if __name__ == "__main__":
    app = create_app()
    serve(app, host="0.0.0.0", port=SERVER_PORT)  # NOSONAR
