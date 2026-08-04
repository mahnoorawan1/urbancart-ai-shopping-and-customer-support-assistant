from flask import Flask
from flask_cors import CORS

from routes.chat import chat_bp

app = Flask(__name__)

CORS(app)

app.register_blueprint(chat_bp)

@app.route("/")
def home():
    return {
        "message": "Welcome to UrbanCart AI Backend 🚀"
    }

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )