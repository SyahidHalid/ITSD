# import webbrowser

# webbrowser.open(r"D:\00. Git Repository\ITSD\CCPT Assessment\dashboard.html")


from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)