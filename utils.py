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
    if file.filename == "":
        flash("Arquivo inválido")
        return redirect(url_for("dashboard"))

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            file.save(tmp.name)
            pdf_text = extract_text_from_pdf(tmp.name)

        if not pdf_text.strip():
            flash("Não foi possível extrair texto do exame")
            return redirect(url_for("dashboard"))

        # Fragmentar e resumir texto
        chunks = split_text_by_tokens(pdf_text)
        summarized_text = summarize_chunks(chunks, client)

        # Prompt final com resumo consolidado
        final_prompt = f"""
        Você é um assistente médico. Recebeu um resumo de exame com os seguintes dados:

        {summarized_text}

        Analise os resultados e retorne:
        - Valores fora do intervalo de referência
        - Lista de possíveis alterações clínicas
        - Possíveis diagnósticos diferenciais (somente sugestões, sem substituir avaliação médica)
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em exames laboratoriais."},
                {"role": "user", "content": final_prompt}
            ],
            max_tokens=600,
            temperature=0.3
        )

        analysis = response.choices[0].message.content.strip()
        return render_template("dashboard.html", result=analysis)

    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
