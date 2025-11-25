from flask import Blueprint, request, jsonify
from groq import Groq
from dotenv import load_dotenv
import os
import re

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Create a blueprint
chat_bp = Blueprint("chat_bp", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("message", "")

    if not msg:
        return jsonify({"error": "Message field is required"}), 400

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Reply in plain text only. No markdown, no bullet points, no numbering."},
                {"role": "user", "content": msg}
            ]
        )

        text = res.choices[0].message.content

        # ---------- CLEANING ----------
        text = re.sub(r'\*\*', '', text)      # remove bold markers
        text = re.sub(r'\n+', ' ', text)      # remove newline
        text = re.sub(r'\d+\.\s*', '', text)  # remove numbered list
        text = re.sub(r'[-•]\s*', '', text)   # remove bullets
        text = text.strip()
        # --------------------------------

        return jsonify({"response": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
