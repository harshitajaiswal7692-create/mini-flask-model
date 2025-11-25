from flask import Flask, request, jsonify
from text import chat_bp  # import blueprint
import os

app = Flask(__name__)
app.register_blueprint(chat_bp)  # register blueprint

# Home Route
@app.route("/", methods=["GET"])
def home():
    return "Flask is running! Use /add or /chat"

# Add Route
@app.route("/add", methods=["POST"])
def add_numbers():
    data = request.get_json()
    a = data.get("a", 0)
    b = data.get("b", 0)
    return jsonify({"a": a, "b": b, "result": a + b})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
