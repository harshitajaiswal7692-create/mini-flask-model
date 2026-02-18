from flask import Blueprint, request, jsonify
from groq import Groq
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import re

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

chat_bp = Blueprint("chat_bp", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    # ✅ Get HTML content from POST
    html_content = data.get("content", "")

    if not html_content:
        return jsonify({"error": "Content field is required"}), 400

    try:

        # ✅ Convert HTML → Plain Text
        soup = BeautifulSoup(html_content, "html.parser")

        # remove unwanted tags
        for tag in soup(["script", "style"]):
            tag.decompose()

        plain_text = soup.get_text(separator=" ").strip()

        # ✅ Send cleaned text to AI
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
                    Generate a summary of EXACTLY 60 words.

                    STRICT RULES:
                    - Output must contain exactly 60 words.
                    - Not less.
                    - Not more.
                    - Plain text only.
                    - Count words carefully before responding.
                    """
                },
                {"role": "user", "content": plain_text}
            ]
        )

        text = res.choices[0].message.content

        # CLEANING (optional)
        text = re.sub(r'\n+', ' ', text).strip()

        return jsonify({"response": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
