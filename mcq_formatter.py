# mcq_formatter.py

def format_mcq(mcqs):
    formatted_texts = []
    for i, mcq in enumerate(mcqs, start=1):
        question = mcq.get("question", "").strip()
        options = mcq.get("options", [])
        correct = mcq.get("answer", "")

        formatted = f"🧠 *Q{i}:* {question}\n\n"
        for j, opt in enumerate(options, start=1):
            formatted += f"{j}. {opt}\n"
        formatted += f"\n✅ *Answer:* ||{correct}||\n\n"  # hidden answer with spoiler
        formatted_texts.append(formatted)

    return formatted_texts
