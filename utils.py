import tiktoken
import tempfile
import os
import pdfplumber

# 1. Extrair texto do PDF
def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    except Exception as e:
        print(f"Erro ao extrair texto do PDF: {e}")
        return ""

# 2. Dividir texto por tokens (usando o modelo GPT-4/gpt-4o-mini)
def split_text_by_tokens(text, max_tokens=1500):
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)

    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk = enc.decode(tokens[i:i + max_tokens])
        chunks.append(chunk)

    return chunks

# 3. Resumir blocos com a API da OpenAI
def summarize_chunks(chunks, client, model="gpt-4o-mini"):
    summaries = []
    for chunk in chunks:
        prompt = f"Resumo clínico do seguinte trecho do exame:\n\n{chunk}\n\nResuma apenas informações clínicas e resultados laboratoriais relevantes."
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Você é um assistente médico especializado em exames."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.3
        )
        summaries.append(response.choices[0].message.content.strip())
    return "\n\n".join(summaries)
