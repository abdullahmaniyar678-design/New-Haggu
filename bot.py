import os, time, json, telebot
from extract import extract_mcqs_from_pdf
from mcq_formatter import format_mcq_message

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Only the admin can upload PDFs.")
        return

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = message.document.file_name
    os.makedirs("temp", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    save_path = os.path.join("temp", filename)
    with open(save_path, "wb") as f:
        f.write(downloaded_file)

    bot.reply_to(message, f"📄 *{filename}* received, extracting MCQs…", parse_mode="Markdown")
    mcqs = extract_mcqs_from_pdf(save_path)

    if not mcqs:
        bot.send_message(message.chat.id, "⚠️ No MCQs found in this file.")
        return

    json_path = os.path.join("output", filename.replace('.pdf', '.json'))
    with open(json_path, "w") as f:
        json.dump(mcqs, f, indent=2)

    bot.send_message(message.chat.id, f"✅ Extracted {len(mcqs)} MCQs. Sending them now…", parse_mode="Markdown")

    current_topic = ""
    MAX_LENGTH = 4000

    def safe_send(text):
        if len(text) > MAX_LENGTH:
            parts = [text[i:i+MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]
            for part in parts:
                bot.send_message(message.chat.id, part, parse_mode="MarkdownV2")
                time.sleep(1)
        else:
            bot.send_message(message.chat.id, text, parse_mode="MarkdownV2")

    for mcq in mcqs:
        topic = mcq.get("topic", "General")
        if topic != current_topic:
            bot.send_message(message.chat.id, f"📘 *Topic:* {topic}", parse_mode="Markdown")
            current_topic = topic

        msg = format_mcq_message(mcq)

        if mcq.get("image"):
            try:
                with open(mcq["image"], "rb") as img:
                    bot.send_photo(message.chat.id, img, caption=msg[:MAX_LENGTH], parse_mode="Markdown")
            except:
                safe_send(msg)
        else:
            safe_send(msg)
        time.sleep(2)

    bot.send_message(message.chat.id, "✅ All MCQs sent successfully!", parse_mode="Markdown")

bot.polling(none_stop=True)
