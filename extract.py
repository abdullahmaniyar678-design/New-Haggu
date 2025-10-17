import fitz  # PyMuPDF
import re
import tempfile
import os

def extract_mcqs_from_pdf(file_path):
    mcqs = []
    try:
        # ✅ Ensure file exists
        if not os.path.exists(file_path):
            print("File not found:", file_path)
            return []

        # ✅ Open the PDF safely
        with fitz.open(file_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text("text")

        # ✅ Normalize lines
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        current_q = {}

        for line in lines:
            # Detect question
            if re.match(r"^(Q\d+|Question\s*\d+|\d+\.)", line, re.IGNORECASE):
                if current_q:
                    mcqs.append(current_q)
                current_q = {"question": line, "options": [], "answer": ""}
            elif re.match(r"^[A-D][\).]", line):  # options like A) or B.
                current_q["options"].append(line)
            elif re.search(r"(?i)\b(ans|answer)\b", line):
                ans_part = line.split(":")[-1].strip()
                current_q["answer"] = ans_part

        if current_q:
            mcqs.append(current_q)

        # ✅ Remove junk entries
        mcqs = [q for q in mcqs if len(q["question"]) > 5]

    except Exception as e:
        print("❌ PDF Extract Error:", e)
        return []

    return mcqs
