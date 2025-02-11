import fitz  # PyMuPDF untuk membaca PDF
import openai
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

# Menggunakan Environment Variable untuk API Key OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Folder untuk menyimpan jurnal
JOURNAL_FOLDER = "journals"
os.makedirs(JOURNAL_FOLDER, exist_ok=True)

# Fungsi untuk membaca teks dari PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# API untuk upload jurnal
@app.route("/upload", methods=["POST"])
def upload_journal():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    file_path = os.path.join(JOURNAL_FOLDER, file.filename)
    file.save(file_path)
    return jsonify({"message": "File uploaded successfully", "file_path": file_path})

# API untuk bertanya ke chatbot
@app.route("/ask", methods=["POST"])
def ask_chatbot():
    data = request.json
    question = data.get("question")
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    # Menggabungkan semua teks dari jurnal yang sudah diunggah
    all_text = ""
    for filename in os.listdir(JOURNAL_FOLDER):
        file_path = os.path.join(JOURNAL_FOLDER, filename)
        all_text += extract_text_from_pdf(file_path) + "\n"
    
    # Prompt untuk OpenAI
    prompt = f"Jurnal berikut berisi:\n{all_text}\n\nPertanyaan: {question}\nJawaban:"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Kamu adalah asisten yang membantu menjawab pertanyaan berdasarkan jurnal."},
                  {"role": "user", "content": prompt}]
    )
    
    answer = response["choices"][0]["message"]["content"].strip()
    return jsonify({"answer": answer})

# Halaman utama untuk chat UI dengan tombol popup chatbot
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
