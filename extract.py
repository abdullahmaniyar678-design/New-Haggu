import fitz  # PyMuPDF

def extract_mcqs_from_pdf(file_path):
    mcqs = []
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text("text")

        # Basic split logic for MCQs (can adjust as needed)
        questions = text.split("\n")
        current_q = {}
        for line in questions:
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith(("q", "question")) or line[0].isdigit():
                if current_q:
                    mcqs.append(current_q)
                current_q = {"question": line, "options": [], "answer": ""}
            elif any(opt in line[:3] for opt in ["A.", "B.", "C.", "D."]):
                current_q["options"].append(line)
            elif "answer" in line.lower() or line.startswith("Ans:"):
                current_q["answer"] = line.split(":")[-1].strip()

        if current_q:
            mcqs.append(current_q)

    except Exception as e:
        print(f"❌ Error while reading PDF: {e}")
        return []

    return mcqs
