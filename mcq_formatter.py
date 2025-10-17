def format_mcq_message(mcq):
    question = f"🧠 *Q:* {mcq['question']}\n"
    options = ""
    correct = mcq['answer']
    for opt in mcq['options']:
        letter = opt[0].upper()
        if letter == correct:
            options += f"✅ {opt}\n"
        else:
            options += f"{opt}\n"
    explanation = f"\n💬 Explanation: ||{mcq['explanation']}||"
    return question + options + explanation
