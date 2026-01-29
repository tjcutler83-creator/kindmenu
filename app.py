import os
from flask import Flask, request, jsonify, redirect
import stripe
from openai import OpenAI

# ------------------
# App setup
# ------------------
app = Flask(__name__)

# ------------------
# Environment variables
# ------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PRICE_MONTHLY = os.getenv("STRIPE_PRICE_MONTHLY")
STRIPE_PRICE_ANNUAL = os.getenv("STRIPE_PRICE_ANNUAL")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

if not STRIPE_SECRET_KEY:
    raise RuntimeError("STRIPE_SECRET_KEY not set")

if not STRIPE_PRICE_MONTHLY or not STRIPE_PRICE_ANNUAL:
    raise RuntimeError("Stripe price IDs not set")

# ------------------
# Clients
# ------------------
client = OpenAI(api_key=OPENAI_API_KEY)
stripe.api_key = STRIPE_SECRET_KEY

# ------------------
# System prompt
# ------------------
SYSTEM_PROMPT = """
You are a helpful assistant that turns restaurant menu ideas
into a clear, well structured menu with descriptions and pricing suggestions.
"""

# ------------------
# Routes
# ------------------

@app.route("/")
def home():
    return "KindMenu backend running"

# -------- AI GENERATE --------
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        menu_text = data.get("menu", "")

        if not menu_text.strip():
            return jsonify({"error": "Menu text is required"}), 400

        response = client.chat.completions.create(
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

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------- STRIPE CHECKOUT --------
@app.route("/checkout/<plan>")
def checkout(plan):
    if plan == "monthly":
        price_id = STRIPE_PRICE_MONTHLY
    elif plan == "annual":
        price_id = STRIPE_PRICE_ANNUAL
    else:
        return "Invalid plan", 400

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1
            }],
            success_url=request.host_url + "?success=true",
            cancel_url=request.host_url + "?canceled=true"
        )

        return redirect(session.url, code=303)

    except Exception as e:
        return f"Stripe error: {e}", 500

# ------------------
# Run locally
# ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
