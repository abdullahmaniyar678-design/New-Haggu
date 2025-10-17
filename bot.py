import os
import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from extract import extract_mcqs_from_pdf
from mcq_formatter import format_mcq
from server import keep_alive  # ✅ Added keep-alive
import math

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# Telegram message limit
MAX_MESSAGE_LENGTH = 4000

# Start keep-alive Flask server
keep_alive()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me a PDF to extract MCQs automatically.")

async def handle_docs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        document = update.message.document
        if not document:
            return await update.message.reply_text("❌ Please send a valid PDF file.")

        # Save PDF temporarily
        file_path = f"temp/{document.file_name}"
        await document.get_file().download_to_drive(file_path)
        await update.message.reply_text(f"📄 PDF '{document.file_name}' received! Extracting MCQs...")

        # Extract MCQs
        mcqs = extract_mcqs_from_pdf(file_path)
        if not mcqs:
            await update.message.reply_text("⚠️ No MCQs found in this PDF.")
            return

        await update.message.reply_text(f"✅ Extracted {len(mcqs)} MCQs. Sending them now...")

        # Send MCQs topic-wise and in message-safe chunks
        topic = "General"
        header_sent = False
        message_buffer = ""

        for i, mcq in enumerate(mcqs, 1):
            # Send topic header only once
            if not header_sent:
                await update.message.reply_text(f"📘 *Topic: {topic}*", parse_mode="Markdown")
                header_sent = True

            formatted_mcq = format_mcq(mcq, i)
            if len(message_buffer) + len(formatted_mcq) > MAX_MESSAGE_LENGTH:
                await update.message.reply_text(message_buffer, parse_mode="Markdown")
                message_buffer = formatted_mcq
            else:
                message_buffer += formatted_mcq + "\n\n"

        # Send remaining MCQs
        if message_buffer:
            await update.message.reply_text(message_buffer, parse_mode="Markdown")

        await update.message.reply_text("✅ All MCQs sent successfully!")

        # Cleanup
        os.remove(file_path)

    except Exception as e:
        logger.error(f"Error handling document: {e}")
        await update.message.reply_text("❌ Error processing your PDF. Please try again later.")

async def send_startup_message(app):
    """Send message to admin when bot starts"""
    if ADMIN_ID:
        try:
            await app.bot.send_message(
                chat_id=ADMIN_ID,
                text="✅ Bot started successfully and is now running 24/7!"
            )
        except Exception as e:
            logger.error(f"Could not send startup message: {e}")

def main():
    # Initialize app
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(MessageHandler(filters.COMMAND & filters.Regex("^/start$"), start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_docs))

    # Notify admin when bot starts
    app.post_init = lambda _: send_startup_message(app)

    # Run bot
    app.run_polling()

if __name__ == "__main__":
    main()
