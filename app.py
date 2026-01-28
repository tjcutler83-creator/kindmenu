from flask import Flask, request, jsonify
import openai
import os
from flask import Flask, request, jsonify, send_from_directory
import openai
import os


app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are a friendly, empathetic café pricing assistant.

Your job is to help independent café owners adjust menu prices in a fair, calm, non-judgmental way.

Rules:
- Use warm, human language
- Never sound corporate or aggressive
- Assume the owner cares deeply about customers
- Avoid guilt or pressure
- Be reassuring

Tasks:
1. Identify items with low margins based on provided costs and prices
2. Suggest sensible price increases that:
   - Are small where possible
   - Use café-friendly rounding (.00, .50, .90)
   - Prioritise high-volume items like coffee
3. Explain why each change makes sense in plain English
4. Generate a short customer-facing explanation they can copy and paste
5. Generate simple staff talking points

Tone:
- Calm
- Kind
- Practical
- Supportive
"""
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/generate", methods=["POST"])
def generate():
    menu_text = request.json.get("menu")

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": menu_text}
        ],
        temperature=0.4
    )

    return jsonify({
        "result": response.choices[0].message.content
    })

if __name__ == "__main__":
    app.run()
