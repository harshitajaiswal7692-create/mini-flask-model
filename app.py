from flask import Flask, request, jsonify

app = Flask(__name__)

# Home route
@app.route("/", methods=["GET"])
def home():
    return "Welcome to the Mini Flask Model!"

# Flask status route
@app.route("/flask", methods=["GET"])
def flask_status():
    return "Flask server running! Use POST /chat"

# Add numbers route
@app.route("/add", methods=["POST"])
def add_numbers():
    data = request.get_json()
    a = data.get("a", 0)
    b = data.get("b", 0)
    result = a + b

    return jsonify({
        "a": a,
        "b": b,
        "result": result
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
