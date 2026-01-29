from flask import Flask, request, jsonify, redirect, send_from_directory
import stripe
import openai
import os

app = Flask(__name__)

# -----------------------------
# CONFIGURATION
# -----------------------------
# Stripe
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Token storage (in-memory)
VALID_TOKENS = set()

# System prompt for AI (replace with your prompt)
SYSTEM_PROMPT = "You are a friendly assistant generating menu items for cafes."

# -----------------------------
# ROUTES
# -----------------------------

# Serve index.html
@app.route("/")
def home():
    # Get folder where app.py lives
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(base_dir, "index.html")


# Generate menu (requires token)
@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    menu_text = data.get("menu")
    token = data.get("token")

    # Check if user has paid
    if token not in VALID_TOKENS:
        return jsonify({"error": "payment_required"}), 402

    # Call OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": menu_text}
        ],
        temperature=0.4
    )

    return jsonify({"result": response.choices[0].message.content})


# Stripe checkout route
@app.route("/checkout/<plan>")
def checkout(plan):
    price_id = os.environ.get("PRICE_MONTHLY") if plan == "monthly" else os.environ.get("PRICE_YEARLY")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=request.host_url + "success",
        cancel_url=request.host_url + "cancel"
    )

    return redirect(session.url, code=303)


# Payment success
@app.route("/success")
def success():
    token = os.urandom(8).hex()
    VALID_TOKENS.add(token)

    return f"""
    <h2>You're all set ☕</h2>
    <p>Your access code:</p>
    <pre>{token}</pre>
    <p>Paste this into KindMenu to unlock it.</p>
    """


# Payment cancelled
@app.route("/cancel")
def cancel():
    return "<h2>Payment cancelled 😕</h2><p>You can try again anytime.</p>"


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

 



   
    


