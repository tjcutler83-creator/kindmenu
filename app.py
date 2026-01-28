from flask import Flask, request, jsonify, redirect, send_from_directory
import stripe
import openai
import os

app = Flask(__name__)

# Stripe configuration
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# In-memory token storage for access control
VALID_TOKENS = set()

openai.api_key = os.getenv("OPENAI_API_KEY")

# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    menu_text = data.get("menu")
    token = data.get("token")  # user must submit the access token

    if token not in VALID_TOKENS:
        return jsonify({"error": "payment_required"}), 402

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": menu_text}
        ],
        temperature=0.4
    )

    return jsonify({"result": response.choices[0].message.content})


@app.route("/checkout/<plan>")
def checkout(plan):
    price_id = os.getenv("PRICE_MONTHLY") if plan == "monthly" else os.getenv("PRICE_YEARLY")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=request.host_url + "success",
        cancel_url=request.host_url + "cancel"
    )

    return redirect(session.url, code=303)


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


@app.route("/cancel")
def cancel():
    return "<h2>Payment cancelled 😕</h2><p>You can try again anytime.</p>"


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


   
    

