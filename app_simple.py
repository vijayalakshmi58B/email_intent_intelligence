from flask import Flask, request, render_template_string

app = Flask(__name__)

INTENTS = ["casual", "congratulation", "meeting_request", "request_invoice"]


def classify_email(text: str):
    t = text.lower()

    invoice_keywords = [
        "invoice", "bill", "billing", "payment receipt", "payment details",
        "amount due", "outstanding payment", "pending payment",
        "send the invoice", "share the invoice", "forward the invoice",
        "request the invoice"
    ]
    if any(k in t for k in invoice_keywords):
        return "request_invoice"

    meeting_keywords = [
        "meeting request", "request a meeting", "schedule a meeting",
        "set up a meeting", "book a meeting", "arrange a meeting",
        "can we meet", "let's meet", "let us meet", "fix a meeting",
        "meeting tomorrow", "meeting on", "catch up for a meeting",
        "zoom call", "teams call", "google meet", "video call",
        "discuss this further", "connect for a call"
    ]
    if any(k in t for k in meeting_keywords):
        return "meeting_request"

    congrats_keywords = [
        "congratulations", "congrats", "well done", "great job",
        "proud of you", "happy for you", "kudos", "big congratulations",
        "heartfelt congratulations", "many congratulations", "you deserve this"
    ]
    if any(k in t for k in congrats_keywords):
        return "congratulation"

    return "casual"


BASE_CSS = """
* {
    box-sizing: border-box;
}
body {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f3f4f8;
    margin: 0;
    padding: 0;
    color: #1f2933;
}
.page {
    max-width: 900px;
    margin: 30px auto;
    padding: 0 16px 30px;
}
.header {
    text-align: center;
    margin-bottom: 24px;
}
.header h1 {
    margin: 0 0 8px;
    font-size: 1.9rem;
}
.subtitle {
    margin: 0;
    color: #555f6d;
    font-size: 0.98rem;
}
.card {
    background: #ffffff;
    border-radius: 14px;
    padding: 18px 20px 20px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}
label {
    display: block;
    margin-bottom: 6px;
    font-weight: 600;
    font-size: 0.9rem;
}
textarea {
    width: 100%;
    padding: 10px 12px;
    border-radius: 10px;
    border: 1px solid #cbd2e1;
    resize: vertical;
    min-height: 220px;
    font-size: 0.95rem;
    font-family: inherit;
}
textarea:focus {
    outline: none;
    border-color: #4a6cf7;
    box-shadow: 0 0 0 1px #4a6cf7;
}
.btn {
    margin-top: 12px;
    padding: 9px 18px;
    border-radius: 999px;
    border: none;
    background: #4a6cf7;
    color: white;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
}
.btn:hover {
    opacity: 0.95;
}
.result {
    margin-top: 18px;
    padding: 12px 14px;
    border-radius: 10px;
    background: #eef2ff;
}
.intent-badge {
    display: inline-block;
    margin-top: 4px;
    padding: 5px 12px;
    border-radius: 999px;
    background: #4338ca;
    color: #fff;
    font-weight: 600;
    font-size: 0.9rem;
}
.footer {
    margin-top: 24px;
    text-align: center;
    font-size: 0.8rem;
    color: #9ca3af;
}
"""


INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Simple Email Intent Classifier</title>
    <style>{{ css }}</style>
</head>
<body>
<div class="page">
    <header class="header">
        <h1>Simple Email Intent Classifier</h1>
        <p class="subtitle">
            Classifies emails into casual, congratulation, meeting_request,
            or request_invoice using simple keywords.
        </p>
    </header>

    <main class="card">
        <h2>Test an Email</h2>
        <form method="POST">
            <label for="email_text">Paste or type an email</label>
            <textarea id="email_text" name="email_text" rows="10"
                      placeholder="Subject: ...&#10;&#10;Dear ...&#10;">{{ email_text }}</textarea>

            <button type="submit" class="btn">Classify Intent</button>
        </form>

        {% if predicted_intent %}
        <div class="result">
            <h3>Predicted Intent</h3>
            <p class="intent-badge">{{ predicted_intent }}</p>
        </div>
        {% endif %}
    </main>

    <footer class="footer">
        <p>Simple Rule-Based Model · One-File Version</p>
    </footer>
</div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    predicted_intent = None
    email_text = ""

    if request.method == "POST":
        email_text = request.form.get("email_text", "")
        if email_text.strip():
            predicted_intent = classify_email(email_text)

    return render_template_string(
        INDEX_TEMPLATE,
        css=BASE_CSS,
        predicted_intent=predicted_intent,
        email_text=email_text,
    )


if __name__ == "__main__":
    app.run(debug=True)
