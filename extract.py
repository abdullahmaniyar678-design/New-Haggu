from PyPDF2 import PdfReader
import re, os

def extract_mcqs_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        try:
            text += page.extract_text() + "\n"
        except:
            pass

    text = re.sub(r'(?is)contents.*?(?=\n\s*Q|Question)', '', text)
    mcq_blocks = re.split(r'(?:\n\s*(?:Q\s*\d+|Question\s*\d+|[\d]+\)))', text)

    os.makedirs("images", exist_ok=True)
    mcqs = []

    for block in mcq_blocks:
        block = block.strip()
        if len(block.split()) < 3:
            continue

        question = block.split("\n")[0].strip()
        options = [l.strip() for l in block.split("\n") if re.match(r'^[A-Da-d][\).\-–\s]', l)]
        if not options:
            continue

        ans_match = re.search(r'Correct\s*Answer[:\-–]?\s*([A-Da-d])', block, re.IGNORECASE)
        correct_letter = ans_match.group(1).upper() if ans_match else None
        exp_match = re.search(r'Explanation[:\-–]?\s*(.*)', block, re.IGNORECASE | re.DOTALL)
        explanation = exp_match.group(1).strip() if exp_match else "Explanation not available."

        mcqs.append({
            "topic": "General",
            "question": question,
            "options": options,
            "answer": correct_letter,
            "explanation": explanation,
            "image": None
        })

    return mcqs
