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

@app.route('/init_user')
def init_user():
    try:
        # Criar as tabelas caso não existam
        db.create_all()

        # Verifica se já existe algum usuário
        if User.query.first():
            return "Usuário inicial já existe."

        # Criar usuário padrão
        senha = generate_password_hash('catupiry136*')
        admin = User(username="brunorei", email="admin@exemplo.com")
        admin.password_hash = senha
        db.session.add(admin)
        db.session.commit()

        return 'Usuário inicial criado com sucesso!'

    except Exception as e:
        return f'Erro ao criar usuário inicial: {e}'







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

@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect(url_for("index"))
    users = User.query.all()
    return render_template("admin.html", users=users)


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
