import os
from flask import Flask, request, jsonify
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Initialize Flask app
text = Flask(__name__)

# Chat generation function
def generate_chat(message):
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": message}]
    )
    return res.choices[0].message.content

# Flask POST endpoint
@text.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "Message field is required"}), 400

    try:
        reply = generate_chat(user_input)
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's port
    text.run(host="0.0.0.0", port=port, debug=False)


