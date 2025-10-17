# bot.py  (replace your current PDF handler with this one)

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from extract import extract_mcqs_from_pdf
from mcq_formatter import format_mcq
import os
import logging

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = await update.message.document.get_file()  # ✅ correct async call
        file_path = f"/tmp/{update.message.document.file_name}"
        await file.download_to_drive(file_path)          # ✅ await download

        mcqs = extract_mcqs_from_pdf(file_path)
        if not mcqs:
            await update.message.reply_text("⚠️ No MCQs found in your PDF.")
            return

        formatted_mcqs = format_mcq(mcqs)
        for text in formatted_mcqs:
            if len(text) > 4000:
                text = text[:3990] + "..."
            await update.message.reply_markdown_v2(text)

    except Exception as e:
        logger.error(f"Error handling document: {e}")
        await update.message.reply_text("❌ Error processing your PDF. Please try again later.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is alive! Send me a PDF to extract MCQs.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.run_polling()
