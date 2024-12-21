from flask import Flask, render_template_string, request, session, redirect, url_for
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required to use session for storing history

API_KEY = "AIzaSyDqXHiorPGyzpRBCLF_drvWwBHlEdu1yho"
CSE_ID = "64d9f57dd8afd493f"

def google_search(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CSE_ID}"
    try:
        response = requests.get(url)
        results = response.json()

        if "items" not in results:
            return "No results found."
    
        response_text = ""
        for item in results["items"][:3]:
            title = item["title"]
            snippet = item["snippet"]
            link = item["link"]
            response_text += f"<strong>{title}</strong><br>{snippet}... <a href='{link}' target='_blank'>Read more</a><br><br>"

        return response_text if response_text else "No results found."

    except Exception as e:
        return f"An error occurred: {e}"


homepage_template = """
<!DOCTYPE html>
<html>
<head>
    <title>QueryBot</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <style>
        body {
            text-align: center;
            background: linear-gradient(135deg, #141e30, #243b55);
            color: #ffffff;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }
        .container {
            padding-top: 10%;
        }
        a {
            text-decoration: none;
            color: #ffffff;
        }
        a:hover {
            text-decoration: underline;
        }
        .btn-primary {
            padding: 10px 20px;
            border-radius: 30px;
            font-size: 1.2rem;
            animation: fadeInUp 1s ease-in-out;
        }
    </style>
</head>
<body>
    <div class="container animate__animated animate__fadeIn">
        <h1 class="display-4">Welcome to QueryBot</h1>
        <p class="lead">Your smart companion for intuitive and precise searches. Dive deep into topics or explore new ideas with ease.</p>
        <p>Developed by <strong>Sharan Rawat</strong></p>
        <a href="{{ url_for('chatbot') }}" class="btn btn-primary">Go to Chatbot</a>
    </div>
    <script>
        gsap.from(".display-4", {duration: 1, y: -50, opacity: 0, ease: "power3.out"});
        gsap.from(".lead", {duration: 1.5, x: -100, opacity: 0, ease: "power3.out", delay: 0.5});
        gsap.from(".btn-primary", {duration: 2, scale: 0.5, opacity: 0, ease: "elastic", delay: 1});
    </script>
</body>
</html>
"""

chatbot_template = """
<!DOCTYPE html>
<html>
<head>
    <title>QueryBot Chat</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #121212; /* Dark background */
            color: #ffffff; /* Light text */
            margin: 0;
            padding: 0;
            overflow-x: hidden;
        }
        .header {
            text-align: center;
            padding: 10px;
            background: linear-gradient(135deg, #1f1f1f, #333333);
            color: #ffffff;
        }
        .chat-container {
            display: flex;
            flex-wrap: wrap;
            height: 100vh;
            overflow: hidden;
        }
        .sidebar {
            width: 25%;
            background-color: #1f1f1f; /* Dark sidebar */
            padding: 20px;
            border-right: 1px solid #333333;
            height: 100%;
            overflow-y: auto;
        }
        .content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .history-item {
            margin-bottom: 10px;
            border-bottom: 1px solid #333333;
            padding: 10px 5px;
            color: #ffffff;
            cursor: pointer;
            border-radius: 4px;
        }
        .history-item:hover {
            background-color: #333333;
        }
        .results {
            padding: 15px;
            border: 1px solid #333333;
            background-color: #1f1f1f;
            color: #ffffff;
            margin-bottom: 20px;
            border-radius: 8px;
            animation: fadeIn 0.5s ease-in-out;
        }
        .footer-form {
            display: flex;
            margin-top: 20px;
        }
        .footer-form input {
            flex: 1;
            padding: 10px;
            margin-right: 10px;
            border-radius: 20px;
            border: 1px solid #333333;
            background-color: #333333;
            color: #ffffff;
        }
        .footer-form button {
            background-color: #007bff;
            color: #ffffff;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
        }
        .footer-form button:hover {
            background-color: #0056b3;
        }
        .btn-danger {
            background-color: #dc3545;
            border: none;
        }
        .btn-danger:hover {
            background-color: #a71d2a;
        }
        /* Scrollbars */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-thumb {
            background-color: #444444;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background-color: #555555;
        }
        @media (max-width: 768px) {
            .sidebar {
                width: 100%;
                height: auto;
                border-right: none;
                border-bottom: 1px solid #333333;
            }
            .content {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="header animate__animated animate__fadeInDown">
        <h2>QueryBot</h2>
    </div>
    <div class="chat-container">
        <div class="sidebar">
            <h4 class="animate__animated animate__fadeInLeft">Chat History</h4>
            {% if history %}
                {% for item in history %}
                <div class="history-item animate__animated animate__fadeInLeft animate__delay-1s">
                    <strong>Query:</strong> {{ item['query'] }}
                </div>
                {% endfor %}
            {% else %}
                <p class="animate__animated animate__fadeIn">No history available.</p>
            {% endif %}
            <form action="{{ url_for('clear_history') }}" method="POST">
                <button type="submit" class="btn btn-danger btn-sm animate__animated animate__fadeIn">Clear History</button>
            </form>
        </div>
        <div class="content">
            <h3 class="animate__animated animate__fadeInRight">How can I help you today?</h3>
            {% if response %}
            <div class="results animate__animated animate__fadeInUp">
                {{ response | safe }}
            </div>
            {% endif %}
            <form method="POST" class="footer-form animate__animated animate__fadeInUp animate__delay-1s">
                <input type="text" name="query" placeholder="Type your query..." required>
                <button type="submit">Search</button>
            </form>
        </div>
    </div>
</body>
</html>
"""



@app.route("/", methods=["GET"])
def homepage():
    return render_template_string(homepage_template)

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if "history" not in session:
        session["history"] = []

    response = ""
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            response = google_search(query)
            session["history"].append({"query": query, "response": response})
            session.modified = True

    return render_template_string(chatbot_template, history=session["history"], response=response)

@app.route("/clear_history", methods=["POST"])
def clear_history():
    session.pop("history", None)
    return redirect(url_for("chatbot"))

if __name__ == "__main__":
    app.run(debug=True)
