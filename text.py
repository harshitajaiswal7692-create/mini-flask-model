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
        max_attempts = 3
        text = ""

        for i in range(max_attempts):

            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Reply in plain text only. No markdown. Summarize into EXACTLY 60 words. Count words carefully."
                    },
                    {"role": "user", "content": msg}
                ]
            )

            text = res.choices[0].message.content

            # CLEANING
            text = re.sub(r'\*\*', '', text)
            text = re.sub(r'\n+', ' ', text)
            text = re.sub(r'\d+\.\s*', '', text)
            text = re.sub(r'[-•]\s*', '', text)
            text = text.strip()

            words = text.split()

            # If too long -> trim
            if len(words) >= 60:
                text = " ".join(words[:60])
                break
            else:
                text = " ".join(words)

        return jsonify({"response": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
