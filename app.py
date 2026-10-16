
from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
import pymupdf
import re

app = Flask(__name__)

# Find the project and data folders
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = BASE_DIR / "pdfs"
print("PDF folder path:", PDF_DIR.resolve())

def extract_text_from_pdf(pdf_path):
    text = ""

    with pymupdf.open(pdf_path) as pdf:
        for page in pdf:
            text += page.get_text() + "\n"

    return text



def load_campus_data():
    print("DEBUG: load_campus_data() was called")
    documents = []

    for filename in [
        "faq.txt",
        "timetable.txt",
        "syllabus.txt",
        "notices.txt"
    ]:
        file_path = DATA_DIR / filename

        if not file_path.exists():
            continue

        text = file_path.read_text(encoding="utf-8")

        if filename in ["syllabus.txt", "faq.txt", "notices.txt"]:
            # Keep each subject or FAQ question-answer pair together
            sections = text.split("\n\n")
        elif filename == "timetable.txt":
            # Keep the day with each timetable entry
            sections = []
            current_day = ""

            for line in text.splitlines():
                line = line.strip()

                if line.endswith(":") and " - " not in line:
                    current_day = line[:-1]
                elif " - " in line and ":" in line:
                    sections.append(f"{current_day}: {line}")
        else:
            # Keep other files line by line
            sections = text.splitlines()

       
        for section in sections:
            section = section.strip()

            if filename == "notices.txt" and section == "Sample College Notices":
                continue

            if filename == "notices.txt" and section.startswith("Note:"):
                continue    

            if section:
                documents.append({
                    "source": filename,
                    "text": section
                })

   
    
           
    return documents


def load_pdf_data():
    documents = []

    if not PDF_DIR.exists():
        return documents

    for pdf_file in PDF_DIR.glob("*.pdf"):
        try:
            with pymupdf.open(pdf_file) as pdf:
                text = "\n".join(
                    page.get_text()
                    for page in pdf
                )
           
            sections = re.split(
    r"(?m)(?=^(?:Library Hours|Computer Lab|Student Help Desk|Sample Event|Purpose)\s*$)",
    text
)


            for section in sections:
                section = section.strip()

                if section:
                    documents.append({
                        "source": pdf_file.name,
                        "text": section
                    })

        except Exception as e:
            print(f"Error reading {pdf_file.name}: {e}")

    return documents



def search_campus_data(question):
    documents = load_campus_data()
    documents.extend(load_pdf_data())

    if not documents:
        return "I couldn't find any campus information files."

    question_lower = question.lower()

    # Give FAQ questions priority
    if any(word in question_lower for word in [
        "unimate", "what information can", "college office",
        "contact the college", "contact details"
    ]):
        faq_documents = [
            doc for doc in documents
            if doc["source"] == "faq.txt"
        ]

        if faq_documents:
            documents = faq_documents

    # Select the appropriate file for the question
    elif any(word in question_lower for word in [
        "timetable", "schedule", "class time", "class timing"
    ]):
        documents = [
            doc for doc in documents
            if doc["source"] == "timetable.txt"
        ]

    elif any(word in question_lower for word in [
        "syllabus", "topic", "topics"
    ]):
        documents = [
            doc for doc in documents
            if doc["source"] == "syllabus.txt"
        ]
    
    elif any(word in question_lower for word in [
        "notice", "notices", "announcement", "announcements"
    ]):
        documents = [
            doc for doc in documents
            if doc["source"] == "notices.txt"
        ]    

    texts = [doc["text"] for doc in documents]
    texts.append(question)

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(texts)

    similarities = cosine_similarity(
        matrix[-1],
        matrix[:-1]
    ).flatten()

    best_index = similarities.argmax()

    if similarities[best_index] == 0:
        return (
            "Sorry, I couldn't find a relevant answer in my campus "
            "information files. Please try asking another question."
        )

    best_document = documents[best_index]
    answer = best_document["text"]

    # Show only the answer from the matching FAQ
    if best_document["source"] == "faq.txt":
        lines = answer.splitlines()

        for line in lines:
            if line.startswith("A:"):
                return line[2:].strip()

    # Clean up syllabus labels
    if best_document["source"] == "syllabus.txt":
        answer = answer.replace("Subject:", "").strip()

    return answer

    answer_parts = []

    
    for document in results:
        text = document["text"]

        if document["source"] == "faq.txt":
            lines = text.splitlines()
            question_line = ""
            answer_line = ""

            for line in lines:
                if line.startswith("Q:"):
                    question_line = line
                elif line.startswith("A:"):
                    answer_line = line

            if question_line and answer_line:
                answer_parts.append(answer_line.replace("A:", "").strip())
            else:
                answer_parts.append(text)

        elif document["source"] == "syllabus.txt":
            text = text.replace("Subject:", "").strip()
            answer_parts.append(text)

        else:
            answer_parts.append(text)

    return "\n\n".join(answer_parts)
    
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("message", "").strip()

    if not question:
        return jsonify({"reply": "Please enter a question."}), 400

    try:
        reply = search_campus_data(question)
        return jsonify({"reply": reply})
    except ValueError:
        return jsonify({
            "reply": (
                "I couldn't process the campus information. "
                "Please check that your text files contain readable text."
            )
        }), 500


    
if __name__ == "__main__":
    question = "Where is the computer lab located?"
    answer = search_campus_data(question)

    print("Test question:", question)
    print("UniMate answer:", answer)

    app.run(debug=True)


    documents = load_campus_data()

    pdf_documents = [
        doc for doc in documents
        if doc["source"].endswith(".pdf")
    ]

    print("PDF documents loaded:", len(pdf_documents))

    for doc in pdf_documents:
        print("PDF filename:", doc["source"])
        print("PDF text preview:", doc["text"][:300])

    app.run(debug=True)