from flask import Flask
from flask_cors import CORS

from routes.chat import chat_bp

app = Flask(__name__)

# Allow requests from the deployed Vercel frontend
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "https://urbancart-ai-assistant.vercel.app"
            ]
        }
    }
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
        debug=False
    )