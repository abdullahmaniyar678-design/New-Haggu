def format_mcq(mcqs):
    formatted = []
    for i, q in enumerate(mcqs, start=1):
        question_text = f"🧠 *Question {i}:* {q.get('question', '').strip()}\n"
        options_text = "\n".join(q.get("options", []))
        answer_text = f"\n\n✅ *Answer:* {q.get('answer', '').strip()}\n"
        formatted.append(question_text + options_text + answer_text)
    return formatted
