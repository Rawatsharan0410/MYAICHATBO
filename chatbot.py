from flask import Flask, render_template_string, request, session, redirect, url_for
import requests

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required to use session for storing history

# Google API details
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
    <title>Welcome to QueryBot</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {
            background-color: #000;
            color: #fff;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 250px;
            text-align: center;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid #444;
        }
        .header a {
            color: #fff;
            text-decoration: none;
            margin-right: 15px;
        }
        .header a:hover {
            text-decoration: underline;
        }
        .main {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 80vh;
            text-align: center;
        }
        h1 {
            font-size: 3em;
            margin-bottom: 20px;
        }
        .btn-container {
            margin-top: 20px;
        }
        .btn-container a {
            margin: 5px;
            padding: 10px 20px;
            color: #000;
            background-color: #fff;
            border: none;
            border-radius: 20px;
            text-decoration: none;
            font-weight: bold;
        }
        .btn-container a:hover {
            background-color: #ddd;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>Welcome to QueryBot</h1>
    <p>Explore the chatbot to get responses.</p>
    <br>
    <p>Developed By Sharan Rawat</p> <br>
    <a href="{{ url_for('chatbot') }}" class="btn btn-primary">Go to Chatbot</a>
</div>

</body>
</html>
"""

chatbot_template = """
<!DOCTYPE html>
<html>
<head>
    <title>QueryBot</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f8f9fa;
            color: #333;
            margin: 0;
            padding: 0;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        .sidebar {
            width: 260px;
            background-color: #f1f1f1;
            padding: 20px;
            overflow-y: auto;
            border-right: 1px solid #ddd;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .sidebar h4 {
            margin: 0 0 10px;
            font-weight: bold;
            font-size: 1.1em;
        }

        .sidebar-item {
            padding: 8px 0;
            color: #333;
            border-bottom: 1px solid #ddd;
            cursor: pointer;
            font-size: 0.95em;
            transition: background-color 0.3s;
        }

        .sidebar-item:hover {
            background-color: #e9ecef;
        }

        .container {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 40px;
            color: #333;
            overflow-y: auto;
        }

        h2 {
            font-size: 2em;
            color: #333;
            font-weight: bold;
            text-align: center;
        }

        .results {
            text-align: left;
            width: 100%;
            max-width: 600px;
            margin: 20px 0;
            padding: 20px;
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
        }

        .footer-form {
            width: 100%;
            max-width: 800px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
        }

        .footer-form input {
            width: 85%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 24px;
            font-size: 1em;
            margin-right: 10px;
        }

        .footer-form button {
            padding: 10px 20px;
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 24px;
            font-size: 1em;
            cursor: pointer;
        }

        .clear-history {
            background-color: #dc3545;
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 24px;
            cursor: pointer;
            margin-bottom: 10px;
            align-self: center;
        }

        /* Responsive layout */
        @media (max-width: 768px) {
            .sidebar {
                width: 100%;
                height: auto;
                border-right: none;
                border-bottom: 1px solid #ddd;
                padding: 10px;
            }
            
            .container {
                padding: 20px;
            }

            .footer-form input {
                width: 100%;
            }
        }
    </style>
</head>
<body>

<div class="sidebar">
    <h4>Chat History</h4>
    {% if history %}
        {% for item in history %}
            <div class="sidebar-item" onclick="loadChat('{{ item['query'] }}', '{{ item['response'] }}')">
                {{ item['query'] }}
            </div>
        {% endfor %}
    {% else %}
        <p>No history available.</p>
    {% endif %}
    <form action="{{ url_for('clear_history') }}" method="POST">
        <button type="submit" class="clear-history">Clear Chat History</button>
    </form>
</div>

<div class="container">
    <h2>What can I help with?</h2>
    
    {% if response %}
    <div class="results">
        <h4>Results:</h4>
        <p>{{ response | safe }}</p>
    </div>
    {% endif %}

    <div class="footer-form">
        <form method="POST">
            <input type="text" name="query" placeholder="Message QueryBot" required>
            <button type="submit">Send</button>
        </form>
    </div>
</div>

<script>
    function loadChat(query, response) {
        alert("Query: " + query + "\\nResponse: " + response);
    }
</script>

<script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def homepage():
    return render_template_string(homepage_template)

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if "history" not in session:
        session["history"] = []

    response = ""
    if request.method == "POST":
        user_query = request.form.get("query")
        response = google_search(user_query)

        # Save query and response in history
        session["history"].append({"query": user_query, "response": response})
        session.modified = True  # Ensure session is updated

    return render_template_string(chatbot_template, response=response, history=session["history"])

@app.route("/clear_history", methods=["POST"])
def clear_history():
    session.pop("history", None)  # Clear chat history from the session
    return redirect(url_for("chatbot"))

if __name__ == "__main__":
    app.run(debug=True)
