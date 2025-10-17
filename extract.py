import fitz  # PyMuPDF
import re

def extract_mcqs_from_pdf(file_path):
    mcqs = []
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text("text")

        # Clean and split lines
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        current_q = {}
        for line in lines:
            # Match Question patterns like Q1, Question 1, or numbers with ?
            if re.match(r"^(Q\d+|Question\s*\d+|\d+\.)", line, re.IGNORECASE):
                if current_q:
                    mcqs.append(current_q)
                current_q = {"question": line, "options": [], "answer": ""}
            elif re.match(r"^[A-D][\).]", line):  # Matches A), B), C), D)
                current_q["options"].append(line)
            elif "answer" in line.lower() or line.startswith("Ans:"):
                current_q["answer"] = line.split(":")[-1].strip()

        if current_q:
            mcqs.append(current_q)

        # Filter out junk like single numbers
        mcqs = [q for q in mcqs if len(q["question"]) > 5]

    except Exception as e:
        print(f"❌ Error while reading PDF: {e}")
        return []

    return mcqs
