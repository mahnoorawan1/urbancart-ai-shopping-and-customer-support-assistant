from flask import Flask
from flask_cors import CORS

from routes.chat import chat_bp

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/chat": {
            "origins": "https://urbancart-ai-assistant.vercel.app"
        }
    },
    methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"]
)

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