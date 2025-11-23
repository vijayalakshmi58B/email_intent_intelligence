from flask import Flask, request, render_template_string

app = Flask(__name__)

# -------------------------------------------------
# 1. Rule-based classifier
# -------------------------------------------------

INTENTS = ["casual", "congratulation", "meeting_request", "request_invoice"]


def classify_email(text: str):
    """
    Classify email and return:
    (predicted_intent, matched_category, matched_keywords)
    """
    t = text.lower()

    # --- request_invoice keywords ---
    invoice_keywords = [
        "invoice", "bill", "billing", "payment receipt", "payment details",
        "amount due", "outstanding payment", "pending payment",
        "send the invoice", "share the invoice", "forward the invoice",
        "request the invoice",
    ]
    matched_invoice = [k for k in invoice_keywords if k in t]
    if matched_invoice:
        return "request_invoice", "request_invoice", matched_invoice

    # --- meeting_request keywords ---
    meeting_keywords = [
        "meeting request", "request a meeting", "schedule a meeting",
        "set up a meeting", "book a meeting", "arrange a meeting",
        "can we meet", "let's meet", "let us meet", "fix a meeting",
        "meeting tomorrow", "meeting on", "catch up for a meeting",
        "zoom call", "teams call", "google meet", "video call",
        "discuss this further", "connect for a call",
    ]
    matched_meeting = [k for k in meeting_keywords if k in t]
    if matched_meeting:
        return "meeting_request", "meeting_request", matched_meeting

    # --- congratulation keywords ---
    congrats_keywords = [
        "congratulations", "congrats", "well done", "great job",
        "proud of you", "happy for you", "kudos", "big congratulations",
        "heartfelt congratulations", "many congratulations", "you deserve this",
    ]
    matched_congrats = [k for k in congrats_keywords if k in t]
    if matched_congrats:
        return "congratulation", "congratulation", matched_congrats

    # Default intent when no rule matches
    return "casual", "casual", []


# -------------------------------------------------
# 2. Evaluation dataset (built in)
# -------------------------------------------------

EVALUATION_DATASET = [
    # casual
    ("Hey, how are you doing?", "casual"),
    ("Just wanted to say hi and check in.", "casual"),
    ("Hope you are doing great. Let's catch up sometime.", "casual"),

    # congratulation
    ("Congratulations on your promotion! You really deserve this.", "congratulation"),
    ("Well done on your excellent performance this semester.", "congratulation"),
    ("Big congratulations on winning the competition!", "congratulation"),

    # meeting_request
    ("I would like to request a meeting to discuss the project updates.", "meeting_request"),
    ("Can we schedule a meeting sometime this week?", "meeting_request"),
    ("Please let me know your availability so we can set up a meeting.", "meeting_request"),

    # request_invoice
    ("Could you please send the invoice for last month’s services?", "request_invoice"),
    ("Kindly share the bill for the recent order.", "request_invoice"),
    ("We need the payment receipt to complete the pending payment.", "request_invoice"),
]


# -------------------------------------------------
# 3. Metrics (pure Python – no sklearn)
# -------------------------------------------------

def compute_metrics(true_labels, pred_labels):
    labels = sorted(set(true_labels))
    total = len(true_labels)
    correct = sum(1 for t, p in zip(true_labels, pred_labels) if t == p)
    accuracy = round(correct / total, 2) if total > 0 else None

    per_label = []
    distribution = []

    for label in labels:
        tp = sum(1 for t, p in zip(true_labels, pred_labels)
                 if t == label and p == label)
        fp = sum(1 for t, p in zip(true_labels, pred_labels)
                 if t != label and p == label)
        fn = sum(1 for t, p in zip(true_labels, pred_labels)
                 if t == label and p != label)

        support = tp + fn
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        per_label.append({
            "label": label,
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1": round(f1, 2),
            "support": support,
        })
        distribution.append({"label": label, "support": support})

    return accuracy, per_label, distribution


def evaluate_classifier():
    if not EVALUATION_DATASET:
        return {"accuracy": None, "per_label": [], "distribution": []}

    texts = [t for t, label in EVALUATION_DATASET]
    true_labels = [label for t, label in EVALUATION_DATASET]
    pred_labels = [classify_email(t)[0] for t in texts]

    accuracy, per_label, distribution = compute_metrics(true_labels, pred_labels)
    return {"accuracy": accuracy, "per_label": per_label, "distribution": distribution}


METRICS = evaluate_classifier()


# -------------------------------------------------
# 4. CSS + HTML templates (inline)
# -------------------------------------------------

BASE_CSS = """
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {
    --bg-gradient: radial-gradient(circle at top left, #eef2ff, #e0f2fe 35%, #fef9c3 70%, #ffffff 100%);
    --card-bg: #ffffff;
    --card-radius: 18px;
    --card-shadow: 0 18px 45px rgba(15, 23, 42, 0.14);
    --primary: #4f46e5;
    --primary-soft: #e0e7ff;
    --primary-dark: #3730a3;
    --accent: #22c55e;
    --text-main: #0f172a;
    --text-muted: #6b7280;
    --border-soft: #e5e7eb;
    --chip-bg: #f9fafb;
}

body {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: var(--bg-gradient);
    min-height: 100vh;
    color: var(--text-main);
}

.page {
    max-width: 1200px;
    margin: 32px auto 40px;
    padding: 0 18px;
}

/* ---------- HEADER ---------- */

.header {
    text-align: center;
    margin-bottom: 26px;
}

.header h1 {
    font-size: 2.1rem;
    letter-spacing: 0.03em;
    font-weight: 800;
    color: #020617;
}

.tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.78rem;
    background: rgba(59, 130, 246, 0.06);
    color: #1d4ed8;
    padding: 4px 12px;
    border-radius: 999px;
    margin-left: 10px;
    border: 1px solid rgba(129, 140, 248, 0.4);
}

.subtitle {
    margin-top: 8px;
    color: var(--text-muted);
    font-size: 0.96rem;
    max-width: 720px;
    margin-left: auto;
    margin-right: auto;
}

/* header button */
.header-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 14px;
}

/* ---------- LAYOUT ---------- */

.layout {
    display: grid;
    grid-template-columns: 1.9fr 1.1fr;
    gap: 20px;
}

.card {
    background: var(--card-bg);
    border-radius: var(--card-radius);
    padding: 20px 22px 22px;
    box-shadow: var(--card-shadow);
    border: 1px solid rgba(148, 163, 184, 0.18);
    backdrop-filter: blur(16px);
}

.main-card h2,
.side-card h2,
.metrics-card h2 {
    margin-bottom: 10px;
    font-size: 1.05rem;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    color: #0f172a;
}

/* ---------- FORM / TEXTAREA ---------- */

label {
    display: block;
    margin-bottom: 6px;
    font-weight: 600;
    font-size: 0.9rem;
    color: #111827;
}

textarea {
    width: 100%;
    padding: 12px 13px;
    border-radius: 14px;
    border: 1px solid #cbd5f5;
    resize: vertical;
    min-height: 230px;
    font-size: 0.95rem;
    font-family: inherit;
    line-height: 1.35;
    background: #f9fafb;
    transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

textarea:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.28);
    background: #ffffff;
}

/* ---------- BUTTONS ---------- */

.btn {
    margin-top: 12px;
    padding: 9px 20px;
    border-radius: 999px;
    border: none;
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    color: white;
    font-size: 0.94rem;
    font-weight: 600;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 12px 25px rgba(79, 70, 229, 0.35);
    transform: translateY(0);
    transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.15s ease;
}

.btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 16px 30px rgba(79, 70, 229, 0.45);
    opacity: 0.96;
}

.secondary-btn {
    background: #ffffff;
    color: var(--primary-dark);
    border: 1px solid rgba(79, 70, 229, 0.5);
    box-shadow: none;
}

.secondary-btn:hover {
    background: var(--primary-soft);
    box-shadow: 0 10px 22px rgba(59, 130, 246, 0.18);
}

/* ---------- RESULT / BADGE ---------- */

.result {
    margin-top: 18px;
    padding: 12px 14px;
    border-radius: 14px;
    background: linear-gradient(135deg, #eef2ff, #e0f2fe);
    border: 1px solid rgba(129, 140, 248, 0.55);
}

.intent-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 6px;
    padding: 6px 14px;
    border-radius: 999px;
    background: #1e293b;
    color: #f9fafb;
    font-weight: 600;
    font-size: 0.88rem;
}

.intent-badge::before {
    content: "";
    width: 9px;
    height: 9px;
    border-radius: 999px;
    background: var(--accent);
}

/* explanation chips */
.explain {
    font-size: 0.84rem;
    color: var(--text-muted);
    margin-top: 8px;
}

.kw-list {
    display: inline-flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-left: 2px;
}

.kw-chip {
    background: rgba(15, 23, 42, 0.06);
    border-radius: 999px;
    padding: 2px 9px;
    font-size: 0.75rem;
    color: #0f172a;
}

/* ---------- SIDE CARD ---------- */

.intent-list {
    list-style: none;
    padding-left: 0;
    margin: 6px 0 14px;
    font-size: 0.9rem;
}

.intent-list li {
    margin-bottom: 8px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
}

.pill {
    width: 11px;
    height: 11px;
    border-radius: 999px;
    margin-top: 6px;
    flex-shrink: 0;
}

.pill-meeting { background: #22c55e; }
.pill-congrats { background: #f97316; }
.pill-invoice { background: #0ea5e9; }
.pill-casual { background: #a855f7; }

.sample-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 8px 0 4px;
}

.chip {
    border-radius: 999px;
    border: 1px solid var(--border-soft);
    padding: 6px 12px;
    background: var(--chip-bg);
    font-size: 0.8rem;
    cursor: pointer;
    transition: background 0.15s ease, transform 0.14s ease, box-shadow 0.14s ease;
}

.chip:hover {
    background: #e0f2fe;
    transform: translateY(-1px);
    box-shadow: 0 10px 18px rgba(15, 23, 42, 0.08);
}

/* ---------- METRICS + TABLE ---------- */

.metrics-card {
    margin-top: 20px;
}

.metrics-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}

.accuracy-line {
    margin: 4px 0 12px;
    font-size: 0.95rem;
}

.table-wrapper {
    overflow-x: auto;
    border-radius: 12px;
    border: 1px solid var(--border-soft);
}

.metrics-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
}

.metrics-table th,
.metrics-table td {
    padding: 7px 9px;
    border-bottom: 1px solid #e5e7eb;
    text-align: left;
}

.metrics-table th {
    background: #f9fafb;
    font-weight: 600;
    color: #111827;
}

.metrics-table tr:nth-child(even) td {
    background: #f9fafb;
}

/* dashboard small cards */

.dashboard-cards {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin: 10px 0 18px;
}

.dash-card {
    flex: 1 1 130px;
    min-width: 150px;
    background: linear-gradient(135deg, #eff6ff, #ecfdf5);
    border-radius: 16px;
    padding: 10px 12px;
    border: 1px solid rgba(148, 163, 184, 0.45);
}

.dash-label {
    display: block;
    font-size: 0.8rem;
    color: var(--text-muted);
}

.dash-value {
    display: block;
    font-size: 1.25rem;
    font-weight: 700;
    margin-top: 3px;
    color: #0f172a;
}

/* chart wrapper */

.chart-container {
    margin-top: 14px;
    max-width: 620px;
}

/* notes + footer */

.note {
    margin-top: 9px;
    font-size: 0.8rem;
    color: var(--text-muted);
}

.footer {
    margin-top: 26px;
    text-align: center;
    font-size: 0.8rem;
    color: #9ca3af;
}

/* ---------- RESPONSIVE ---------- */

@media (max-width: 900px) {
    .layout {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 640px) {
    .page {
        padding: 0 12px 22px;
        margin-top: 20px;
    }

    .header h1 {
        font-size: 1.6rem;
    }

    .card {
        padding: 16px 14px 18px;
    }
}
"""

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Email Intent Intelligence - Rule-Based</title>
    <style>{{ css }}</style>
</head>
<body>
<div class="page">
    <header class="header">
        <h1>Email Intent Intelligence <span class="tag">Rule-Based Automation</span></h1>
        <p class="subtitle">
            Classifies emails into <strong>casual</strong>,
            <strong>congratulation</strong>, <strong>meeting_request</strong>,
            or <strong>request_invoice</strong> using transparent keyword rules
            and a built-in analytics dashboard.
        </p>

        <a href="{{ url_for('dashboard') }}" class="btn secondary-btn header-btn">
            Open Dashboard
        </a>
    </header>

    <section class="layout">
        <main class="card main-card">
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

                <h4>Why this label?</h4>
                {% if matched_keywords %}
                    <p class="explain">
                        Matched rule category: <strong>{{ matched_category }}</strong><br>
                        Trigger keywords:
                        <span class="kw-list">
                        {% for kw in matched_keywords %}
                            <span class="kw-chip">{{ kw }}</span>
                        {% endfor %}
                        </span>
                    </p>
                {% else %}
                    <p class="explain">
                        No specific rule keywords matched. The email is treated as
                        <strong>casual</strong>.
                    </p>
                {% endif %}
            </div>
            {% endif %}
        </main>

        <aside class="card side-card">
            <h2>Supported Intents</h2>
            <ul class="intent-list">
                <li><span class="pill pill-meeting"></span> <strong>meeting_request</strong> – emails that ask to schedule or request a meeting or call.</li>
                <li><span class="pill pill-congrats"></span> <strong>congratulation</strong> – emails that celebrate or praise someone's achievement.</li>
                <li><span class="pill pill-invoice"></span> <strong>request_invoice</strong> – emails that ask for an invoice, bill, or payment details.</li>
                <li><span class="pill pill-casual"></span> <strong>casual</strong> – general informal messages that do not match the above rules.</li>
            </ul>

            <h2>Try Sample Emails</h2>
            <div class="sample-buttons">
                <button type="button" class="chip" onclick="fillSample('meeting')">Sample: Meeting Request</button>
                <button type="button" class="chip" onclick="fillSample('congrats')">Sample: Congratulations</button>
                <button type="button" class="chip" onclick="fillSample('invoice')">Sample: Request Invoice</button>
                <button type="button" class="chip" onclick="fillSample('casual')">Sample: Casual</button>
            </div>

            <p class="note">
                This project is completely <strong>rule-based</strong> (no ML model),
                making it easy to explain and safe for small datasets.
            </p>
        </aside>
    </section>

    <section class="card metrics-card">
        <div class="metrics-header-row">
            <h2>Quick Metrics Overview</h2>
        </div>

        {% if metrics and metrics.accuracy is not none %}
        <p class="accuracy-line">
            Overall accuracy on built-in labelled examples:
            <strong>{{ metrics.accuracy }}</strong>
        </p>

        <div class="table-wrapper">
            <table class="metrics-table">
                <thead>
                    <tr>
                        <th>Label</th>
                        <th>Precision</th>
                        <th>Recall</th>
                        <th>F1-score</th>
                        <th>Support</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in metrics.per_label %}
                    <tr>
                        <td>{{ row.label }}</td>
                        <td>{{ row.precision }}</td>
                        <td>{{ row.recall }}</td>
                        <td>{{ row.f1 }}</td>
                        <td>{{ row.support }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <p class="note">
            No evaluation data found.
        </p>
        {% endif %}
    </section>

    <footer class="footer">
        <p>Email Intent Intelligence · Rule-Based Hackathon Project</p>
    </footer>
</div>

<script>
function fillSample(type) {
    const textarea = document.getElementById('email_text');
    let text = '';

    if (type === 'meeting') {
        text = `Subject: Meeting request

Dear Rahul,

I hope you are doing well. I would like to request a meeting with you to discuss the project updates.
Please let me know your availability this week so that we can schedule a meeting or a short video call.`;
    } else if (type === 'congrats') {
        text = `Subject: Congratulations on your achievement

Dear Anjali,

Congratulations on your wonderful achievement! Your hard work and dedication have really paid off.
I am proud of you and wish you even more success ahead.`;
    } else if (type === 'invoice') {
        text = `Subject: Request for invoice

Dear Accounts Team,

I hope you are doing well. Could you please send the invoice for last month’s services?
We require the bill to complete the pending payment and update our records.`;
    } else if (type === 'casual') {
        text = `Subject: Just checking in

Hey Priya,

I hope you are doing great. Just wanted to say hi and see how things are going with you.
Let me know when you are free to catch up.`;
    }

    textarea.value = text;
}
</script>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Email Intent Dashboard</title>
    <style>{{ css }}</style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
<div class="page">
    <header class="header">
        <h1>Email Intent Dashboard</h1>
        <p class="subtitle">
            Overview of classifier performance on the built-in labelled dataset.
        </p>
        <a href="{{ url_for('index') }}" class="btn secondary-btn header-btn">
            ← Back to Classifier
        </a>
    </header>

    <section class="card metrics-card">
        {% if metrics and metrics.accuracy is not none %}
        <div class="metrics-header-row">
            <h2>Summary</h2>
        </div>

        <div class="dashboard-cards">
            <div class="dash-card">
                <span class="dash-label">Accuracy</span>
                <span class="dash-value">{{ metrics.accuracy }}</span>
            </div>
            <div class="dash-card">
                <span class="dash-label">Total Samples</span>
                <span class="dash-value">
                    {{ metrics.per_label | sum(attribute='support') }}
                </span>
            </div>
            <div class="dash-card">
                <span class="dash-label">Number of Intents</span>
                <span class="dash-value">
                    {{ metrics.per_label | length }}
                </span>
            </div>
        </div>

        <h2>Per-label Metrics</h2>
        <div class="table-wrapper">
            <table class="metrics-table">
                <thead>
                    <tr>
                        <th>Label</th>
                        <th>Precision</th>
                        <th>Recall</th>
                        <th>F1-score</th>
                        <th>Support</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in metrics.per_label %}
                    <tr>
                        <td>{{ row.label }}</td>
                        <td>{{ row.precision }}</td>
                        <td>{{ row.recall }}</td>
                        <td>{{ row.f1 }}</td>
                        <td>{{ row.support }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <h2>Label Distribution</h2>
        <div class="chart-container">
            <canvas id="distChart"></canvas>
        </div>

        <p class="note">
            Data is defined directly inside <code>EVALUATION_DATASET</code> in <code>app_full.py</code>.
            You can add more labelled emails there to update the dashboard.
        </p>
        {% else %}
        <p class="note">No evaluation data found.</p>
        {% endif %}
    </section>

    <footer class="footer">
        <p>Email Intent Intelligence · Dashboard View</p>
    </footer>
</div>

{% if metrics and metrics.distribution %}
<script>
    const labels = [
        {% for row in metrics.distribution %}
            "{{ row.label }}",
        {% endfor %}
    ];
    const counts = [
        {% for row in metrics.distribution %}
            {{ row.support }},
        {% endfor %}
    ];

    const ctx = document.getElementById('distChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of samples',
                data: counts
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
</script>
{% endif %}
</body>
</html>
"""


# -------------------------------------------------
# 5. Routes
# -------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    predicted_intent = None
    matched_category = None
    matched_keywords = []
    email_text = ""

    if request.method == "POST":
        email_text = request.form.get("email_text", "")
        if email_text.strip():
            predicted_intent, matched_category, matched_keywords = classify_email(email_text)

    return render_template_string(
        INDEX_TEMPLATE,
        css=BASE_CSS,
        predicted_intent=predicted_intent,
        matched_category=matched_category,
        matched_keywords=matched_keywords,
        email_text=email_text,
        metrics=METRICS,
    )


@app.route("/dashboard")
def dashboard():
    metrics = evaluate_classifier()
    return render_template_string(
        DASHBOARD_TEMPLATE,
        css=BASE_CSS,
        metrics=metrics,
    )


if __name__ == "__main__":
    app.run(debug=True)