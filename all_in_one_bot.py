# all_in_one_bot.py
import os
import telebot
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID"))    # your personal Telegram user id
GROUP_ID = int(os.getenv("GROUP_ID"))              # your group id (starts with -100 for supergroups)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# restart loop so small crashes auto-restart inside process
while True:
    try:
        @bot.message_handler(commands=['start'])
        def start_cmd(msg):
            bot.reply_to(msg, "👋 Send me your screenshot!")

        @bot.message_handler(content_types=['photo'])
        def handle_photo(message):
            username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
            photo_file_id = message.photo[-1].file_id
            caption = f"📸 Screenshot from {username}"
            # re-send as a new message from bot (no 'forwarded from')
            bot.send_photo(GROUP_ID, photo_file_id, caption=caption)
            bot.reply_to(message, "✅ Screenshot received and posted!")
            # optional notify owner privately
            try:
                bot.send_message(OWNER_CHAT_ID, f"📤 Screenshot received from {username}")
            except Exception:
                pass

        @bot.message_handler(content_types=['text'])
        def handle_text(message):
            # If you (owner) send text to bot, post it to group
            if message.chat.id == OWNER_CHAT_ID:
                bot.send_message(GROUP_ID, message.text)
                bot.reply_to(message, "📤 Posted to group.")
            else:
                # other users -> forward as message to group (or handle differently)
                username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
                bot.send_message(GROUP_ID, f"💬 Message from {username}:\n\n{message.text}")
                bot.reply_to(message, "✅ Message sent to owner/group.")

        print("🤖 Bot starting (polling)...")
        bot.infinity_polling()
    except Exception as e:
        print("⚠️ Bot crashed, restarting in 5s:", e)
        time.sleep(5)
