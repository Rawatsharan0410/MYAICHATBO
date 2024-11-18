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
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {
            text-align: center;
            background-color: #000;
            color: #fff;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        .container {
            padding-top: 15%;
        }
        a {
            text-decoration: none;
            color: white;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to QueryBot</h1>
        <p>Making your questions smarter and your searches more intuitive, one query at a time. With every search, we aim to simplify the journey from curiosity to discovery, ensuring precision, clarity, and relevance in the answers you seek. This platform is a testament to the power of innovation and passion, designed to transform the way you access information. Whether you’re exploring new ideas or diving deep into a topic, we’re here to empower your searches with intelligence and ease, all while providing an engaging, user-friendly experience.</p>
        <p>Developed by Sharan Rawat</p>
        <a href="{{ url_for('chatbot') }}" class="btn btn-primary">Go to Chatbot</a>
    </div>
</body>
</html>
"""

chatbot_template = """
<!DOCTYPE html>
<html>
<head>
    <title>QueryBot Chat</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #121212; /* Dark background */
            color: #ffffff; /* Light text */
            margin: 0;
            padding: 0;
        }
        .header {
            text-align: center;
            padding: 10px;
            background-color: #1f1f1f; /* Darker header */
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
    <div class="header">
        <h2>QueryBot</h2>
    </div>
    <div class="chat-container">
        <div class="sidebar">
            <h4>Chat History</h4>
            {% if history %}
                {% for item in history %}
                <div class="history-item">
                    <strong>Query:</strong> {{ item['query'] }}
                </div>
                {% endfor %}
            {% else %}
                <p>No history available.</p>
            {% endif %}
            <form action="{{ url_for('clear_history') }}" method="POST">
                <button type="submit" class="btn btn-danger btn-sm">Clear History</button>
            </form>
        </div>
        <div class="content">
            <h3>How can I help you today?</h3>
            {% if response %}
            <div class="results">
                {{ response | safe }}
            </div>
            {% endif %}
            <form method="POST" class="footer-form">
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