import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import requests
from pdfminer.high_level import extract_text
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

app = Flask(__name__)

CORS(app)

# Chave Openai
openai.api_key = ""

def truncate_text(text, max_length):
    if len(text) > max_length:
        return text[:max_length]
    return text


def pdf_to_text_image(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""

    for image in images:
        text += pytesseract.image_to_string(image)

    return text

def convert_pdf_to_txt(pdf_path):
    text_based = extract_text(pdf_path)

    # Verifica se o texto extraído está vazio, o que pode indicar que o PDF é baseado em imagem
    if not text_based.strip():
        return pdf_to_text_image(pdf_path)
    else:
        return text_based
    
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    # Create the directory if it doesn't exist
    if not os.path.exists("uploaded_files"):
        os.makedirs("uploaded_files")

    files = request.files.getlist("file")
    prompts = request.form.getlist("prompt")
    job_description = request.form.get("job_description")

    responses = {}

    for file in files:
        file_path = os.path.join("uploaded_files", file.filename)
        file.save(file_path)

        max_length = 2048
        resume_text = convert_pdf_to_txt(file_path)
        resume_text = truncate_text(resume_text, max_length)

        file_responses = []

        for prompt in prompts:
            messages = [
                {"role": "system", "content": f"Com base na descrição da vaga fornecida, analise o seguinte currículo para identificar se o candidato possui experiência na exata tecnologia: {prompt}. Retorne um “ok” se a pessoa atende aos requisitos ou um “não ok” se não atende. Descrição da vaga: {job_description}"},
                {"role": "user", "content": f"{resume_text}"}
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3
            )

            message = response['choices'][0]['message']['content']

            # Check if the message indicates approval or rejection
            approval = "Reprovado" if "não ok" in message.lower() else "Aprovado"

            file_responses.append({
                'prompt': prompt,
                'approval': approval,
                'reason': message  # Return the message from GPT-3 as the reason
            })

        responses[file.filename] = file_responses

    return jsonify(responses)


if __name__ == '__main__':
    app.run()
