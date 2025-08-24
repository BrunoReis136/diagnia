from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import timedelta


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=30)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # Validação fictícia (depois pode integrar banco de dados)
    if username == "medico" and password == "123":
        session["user"] = username
        flash("Login realizado com sucesso!", "success")
        return redirect(url_for("dashboard"))
    else:
        flash("Usuário ou senha inválidos", "danger")
        return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("index"))
    return f"Bem-vindo, Dr(a). {session['user']}! Aqui ficará o painel."

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    flash("Você saiu com sucesso.", "info")
    return redirect(url_for("index"))




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
