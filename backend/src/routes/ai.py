from flask import Blueprint, request, jsonify
from src.services.ai_service import AIService

ai_bp = Blueprint("ai", __name__)
ai_service = AIService()

@ai_bp.route("/generate-content", methods=["POST"])
def generate_content():
    data = request.get_json()
    prompt = data.get("prompt")
    content_type = data.get("content_type", "article") # e.g., article, summary, explanation
    
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        if content_type == "article":
            generated_text = ai_service.generate_article(prompt)
        elif content_type == "summary":
            generated_text = ai_service.summarize_content(prompt)
        elif content_type == "explanation":
            generated_text = ai_service.answer_question(prompt)
        else:
            return jsonify({"error": "Invalid content type"}), 400

        return jsonify({"generated_content": generated_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


