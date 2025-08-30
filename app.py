from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import timedelta
from models import db, Medico
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import text
from utils import extract_text_from_pdf, split_text_by_tokens, summarize_chunks, count_tokens
import tempfile
from openai import OpenAI


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=30)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

db.init_app(app)
with app.app_context():
    db.create_all()


@app.route("/reset_table")
def reset_table():
    try:
        db.session.execute(text("""DROP TABLE IF EXISTS users CASCADE;"""))
        db.session.commit()
        db.create_all()
        flash("operação realizada", "success")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Falha : {e}","danger")
        return redirect(url_for("index"))
        

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/institucional", methods=["GET"])
def institucional():
    return render_template("institucional.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")  # pode ser nome ou CRM
    password = request.form.get("password")

    # Buscar médico pelo nome OU pelo CRM
    medico = Medico.query.filter(
        (Medico.nome == username) | (Medico.crm == username)
    ).first()

    if medico and medico.check_password(password):
        session["medico_id"] = medico.id
        session["medico_nome"] = medico.nome
        flash("Login realizado com sucesso!", "success")
        return redirect(url_for("dashboard"))
    else:
        flash("Nome/CRM ou senha inválidos", "danger")
        return redirect(url_for("index"))



@app.route("/dashboard")
def dashboard():
    if "medico_nome" not in session:
        return redirect(url_for("index"))
    return render_template("dashboard.html", result=None)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("medico_nome", None)
    flash("Você saiu com sucesso.", "info")
    return redirect(url_for("index"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    # Se já estiver logado como admin, mostra o painel
    if session.get("admin_logged_in"):
        medicos = Medico.query.all()  # pega todos os usuários
        return render_template("admin.html", admin=True, medicos=medicos)

    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        ADM_USER = os.getenv("ADM_USER")
        ADM_PASSWORD = os.getenv("ADM_PASSWORD")

        if username == ADM_USER and password == ADM_PASSWORD:
            session["admin_logged_in"] = True
            flash("Login de administrador realizado com sucesso!", "success")
            medicos = Medico.query.all()
            return render_template("admin.html", admin=True, medicos=medicos)
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



@app.route("/add_medico", methods=["POST"])
def add_medico():
    nome = request.form.get("nome")
    crm = request.form.get("crm")
    email = request.form.get("email")
    especialidade = request.form.get("especialidade")
    password = request.form.get("password")

    # Criar objeto médico
    novo_medico = Medico(
        nome=nome,
        crm=crm,
        email=email,
        especialidade=especialidade
    )
    novo_medico.set_password(password)

    db.session.add(novo_medico)
    db.session.commit()

    flash("Médico cadastrado com sucesso!", "success")
    return redirect(url_for("admin"))

from flask import request, redirect, url_for, flash, render_template
import tempfile, os

# Importa as funções utilitárias
from utils import extract_text_from_pdf, split_text_by_tokens, summarize_chunks

@app.route("/exame_result", methods=["POST"])
def exame_result():
    if "file" not in request.files:
        flash("Nenhum arquivo enviado")
        return redirect(url_for("dashboard"))

    file = request.files["file"]
    detalhes = request.form.get("detalhes", "").strip().replace("\n", " ")

    if len(detalhes) > 200:
        flash("O campo de detalhes não pode ultrapassar 200 caracteres.")
        return redirect(url_for("dashboard"))

    if file.filename == "":
        flash("Arquivo inválido")
        return redirect(url_for("dashboard"))

    if not file.filename.lower().endswith(".pdf") or file.content_type != "application/pdf":
        flash("Apenas arquivos PDF são permitidos")
        return redirect(url_for("dashboard"))

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp_path = tmp.name
            file.save(tmp_path)
            pdf_text = extract_text_from_pdf(tmp_path)

        if not pdf_text.strip():
            flash("Não foi possível extrair texto do exame")
            return redirect(url_for("dashboard"))

        token_count = count_tokens(pdf_text)

        if token_count > 1500:
            chunks = split_text_by_tokens(pdf_text)
            summarized_text = summarize_chunks(chunks, client)
            final_text = summarized_text
        else:
            final_text = pdf_text

        final_prompt = f"""
Você é um assistente médico. Recebeu um exame com os seguintes detalhes:

{detalhes}

E os seguintes dados extraídos do exame:

{final_text}

Analise os resultados e retorne com clareza e objetividade:

1. Valores fora do intervalo de referência (resuma em até 500 caracteres)
2. Possíveis alterações clínicas com base nos dados (resuma em até 500 caracteres)
3. Diagnósticos diferenciais sugeridos (resuma em até 500 caracteres — apenas sugestões, sem substituir avaliação médica)

Responda em português, de forma direta e médica.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente médico. Responda com objetividade, em português, e siga exatamente os limites de caracteres indicados pelo usuário."
                    },
                    {
                        "role": "user",
                        "content": final_prompt
                    }
                ],
                max_tokens=600,
                temperature=0.3
            )
            analysis = response.choices[0].message.content.strip()
            return render_template("dashboard.html", result=analysis)

        except Exception as e:
            flash("Erro ao processar com a inteligência artificial. Tente novamente.")
            print(f"[Erro OpenAI] {e}")
            return redirect(url_for("dashboard"))

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)






if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
