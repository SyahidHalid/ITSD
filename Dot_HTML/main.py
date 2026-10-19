#   !pip install flask --trusted-host pypi.org --trusted-host files.pythonhosted.org


# import webbrowser

# webbrowser.open(r"D:\00. Git Repository\ITSD\CCPT Assessment\dashboard.html")

#   http://127.0.0.1:5000/
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/ccpt")
def ccpt():
    return render_template("ccpt.html")


if __name__ == "__main__":
    app.run(debug=True)