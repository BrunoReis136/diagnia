from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import timedelta
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=30)


db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # Buscar usuário no banco
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session["user"] = user.username
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

from models import User

@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Se já estiver logado como admin, mostra o painel
    if session.get("admin_logged_in"):
        users = User.query.all()  # pega todos os usuários
        return render_template("admin.html", admin=True, users=users)

    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        ADM_USER = os.getenv("ADM_USER")
        ADM_PASSWORD = os.getenv("ADM_PASSWORD")

        if username == ADM_USER and password == ADM_PASSWORD:
            session["admin_logged_in"] = True
            flash("Login de administrador realizado com sucesso!", "success")
            users = User.query.all()
            return render_template("admin.html", admin=True, users=users)
        else:
            error = "Usuário ou senha inválidos."
            flash(error, "danger")

    # Se GET ou login falhou
    return render_template("admin.html", admin=False)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Logout realizado com sucesso!", "info")
    return redirect(url_for("admin"))



@app.route("/add_user", methods=["POST"])
def add_user():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if User.query.filter_by(username=username).first():
        flash("Usuário já existe!", "danger")
        return redirect(url_for("admin"))

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    flash("Usuário cadastrado com sucesso!", "success")
    return redirect(url_for("admin"))





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
