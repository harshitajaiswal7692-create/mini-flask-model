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

    html_content = data.get("content", "")

    if not html_content:
        return jsonify({"error": "Content field is required"}), 400

    try:

        soup = BeautifulSoup(html_content, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        plain_text = soup.get_text(separator=" ").strip()

        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
                    Reply in plain text only.
                    Summarize the content in up to 60 words.
                    Do not exceed 60 words.
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
