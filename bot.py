import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

ADMINS = {509049673}

staff = {
    "Кальянные мастера": {
        "Егор 🔥": None,
        "Женя 🔥": None,
        "Илья 🔥": None,
        "Дима 🔥": None,
        "Паша 🔥": None,
        "Денис 🔥": None
    },
    "Администраторы": {
        "Алина 🌿": None,
        "Арина 🌿": None,
        "Катя 🌿": None,
        "Кристина 🌿": None
    }
}

WELCOME_MESSAGE = (
    "Здравствуй 🤍, это специальный бот от нашего заведения, "
    "благодаря которому ты сможешь поблагодарить чаевыми кого-то из ребят за их работу. 🫶🏻\n"
    "Кому сегодня хочется сказать «спасибо»?"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MESSAGE, reply_markup=main_menu())

def main_menu():
    keyboard = [
        [InlineKeyboardButton("Кальянные мастера", callback_data="hookah")],
        [InlineKeyboardButton("Администраторы", callback_data="admins")]
    ]
    return InlineKeyboardMarkup(keyboard)

def generate_staff_keyboard(group):
    keyboard = [
        [InlineKeyboardButton(name, callback_data=f"user|{group}|{name}")]
        for name in staff[group]
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "hookah":
        await query.edit_message_text("Выбери мастера:", reply_markup=generate_staff_keyboard("Кальянные мастера"))
    elif query.data == "admins":
        await query.edit_message_text("Выбери администратора:", reply_markup=generate_staff_keyboard("Администраторы"))
    elif query.data == "back":
        await query.edit_message_text(WELCOME_MESSAGE, reply_markup=main_menu())
    elif query.data.startswith("user|"):
        _, group, name = query.data.split("|")
        link = staff[group][name]
        if link:
            await query.edit_message_text(f"Вот ссылка для чаевых для {name}:\n{link}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data=group.lower())]]))
        else:
            await query.edit_message_text(f"{name} пока не добавил ссылку для чаевых 😔", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data=group.lower())]]))

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Извини, я не понял команду. Используй /start 🙂")

if __name__ == "__main__":
    token = os.getenv("TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("Бот запущен...")
    app.run_polling()
