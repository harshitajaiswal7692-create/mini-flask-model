from flask import Blueprint, request, jsonify
from groq import Groq
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import re

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

chat_bp = Blueprint("chat_bp", __name__)

def count_words(text):
    """Helper function to count words in text"""
    return len(text.split())

def enforce_word_count(text, target_word_count=60):
    """Ensure text has exactly target_word_count words"""
    words = text.split()
    current_count = len(words)
    
    if current_count == target_word_count:
        return text
    elif current_count > target_word_count:
        # Truncate to exact word count
        return ' '.join(words[:target_word_count])
    else:
        # If too short, return as is (the AI should handle this, but just in case)
        return text

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    # Get HTML content from POST
    html_content = data.get("content", "")

    if not html_content:
        return jsonify({"error": "Content field is required"}), 400

    try:
        # Convert HTML to Plain Text
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove unwanted tags
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        plain_text = soup.get_text(separator=" ").strip()
        
        # Clean up extra whitespace
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()

        # Send cleaned text to AI with enhanced instructions
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are a precise summarization assistant. Generate a summary of EXACTLY 60 words.

                    CRITICAL REQUIREMENTS:
                    - The summary MUST contain EXACTLY 60 words - no more, no less
                    - Count every word meticulously before outputting
                    - Capture the main ideas and key points concisely
                    - Use clear, professional language
                    - Output only the summary text, no explanations or additional content
                    - Double-check your word count before responding

                    Word count verification process:
                    1. Write the summary
                    2. Count every word
                    3. If count ≠ 60, adjust until EXACTLY 60
                    4. Only then output the result
                    """
                },
                {"role": "user", "content": f"Summarize this content in exactly 60 words:\n\n{plain_text}"}
            ]
        )

        # Get AI response
        text = res.choices[0].message.content

        # Clean the text
        text = re.sub(r'\n+', ' ', text).strip()
        text = re.sub(r'\s+', ' ', text).strip()

        # Enforce exact word count
        final_text = enforce_word_count(text, 60)
        
        # Final verification
        word_count = count_words(final_text)
        
        # Prepare response with metadata
        response_data = {
            "response": final_text,
            "word_count": word_count,
            "status": "success" if word_count == 60 else f"warning: {word_count} words"
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Optional: Add a test endpoint
@chat_bp.route("/test-summary", methods=["POST"])
def test_summary():
    """Test endpoint to verify word count"""
    data = request.get_json()
    test_text = data.get("text", "")
    
    if not test_text:
        return jsonify({"error": "Text field is required"}), 400
    
    word_count = count_words(test_text)
    
    return jsonify({
        "text": test_text,
        "word_count": word_count,
        "exactly_60": word_count == 60
    })