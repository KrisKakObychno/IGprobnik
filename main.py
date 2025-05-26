
import os
from datetime import datetime, timedelta
import telebot
from telebot import types
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# ==== Настройки ====
admin_ids = [509049673]  # Твой Telegram ID — замени на свой
staff = {
    'venue': {},   # Заведение
    'hookah': {},  # Кальянные мастера
    'admin': {}    # Администраторы
}

welcome_message = "Добро пожаловать! ✨ Это специальный бот нашего заведения, чтобы поблагодарить чаевыми."
delayed_message = "Если вам у нас понравилось, можете оставить отзыв о нас в 2ГИС, будем рады! ☺️"

# ==== Планировщик ====
scheduler = BackgroundScheduler()
scheduler.start()

# ==== Проверка админа ====
def is_admin(user_id):
    return user_id in admin_ids

# ==== Команда /start ====
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, welcome_message)

    scheduler.add_job(
        lambda: bot.send_message(message.chat.id, delayed_message),
        'date',
        run_date=datetime.now() + timedelta(seconds=60),
        id=str(message.chat.id),
        replace_existing=True  # <-- исправление: предотвращает конфликт ID
    )

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Заведение", "Кальянный мастер💨", "Менеджер💫")
    bot.send_message(message.chat.id, "Кого вы желаете отблагодарить?", reply_markup=markup)

# ==== Обработка выбора роли ====
@bot.message_handler(func=lambda m: m.text in ["Заведение", "Кальянный мастер💨", "Менеджер💫"])
def handle_role(message):
    role_map = {
        "Заведение": "venue",
        "Кальянный мастер💨": "hookah",
        "Менеджер💫": "admin"
    }
    role = role_map[message.text]
    if staff[role]:
        response = "Выберите сотрудника:\n"
        for name, link in staff[role].items():
            response += f"{name}: {link}\n"
    else:
        response = "Пока нет добавленных сотрудников."
    bot.send_message(message.chat.id, response)

# ==== Команда /add — добавить сотрудника ====
@bot.message_handler(commands=['add'])
def add_staff(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, role, name, link = message.text.split(maxsplit=3)
        if role in staff:
            staff[role][name] = link
            bot.reply_to(message, f"{name} добавлен в {role}!")
        else:
            bot.reply_to(message, "Роль должна быть: venue, hookah или admin.")
    except:
        bot.reply_to(message, "Используйте формат: /add [role] [name] [link]")

# ==== Команда /remove — удалить сотрудника ====
@bot.message_handler(commands=['remove'])
def remove_staff(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, role, name = message.text.split(maxsplit=2)
        if role in staff and name in staff[role]:
            del staff[role][name]
            bot.reply_to(message, f"{name} удалён из {role}.")
        else:
            bot.reply_to(message, "Такой сотрудник не найден.")
    except:
        bot.reply_to(message, "Используйте формат: /remove [role] [name]")

# ==== Команда /setwelcome ====
@bot.message_handler(commands=['setwelcome'])
def set_welcome(message):
    if not is_admin(message.from_user.id):
        return
    global welcome_message
    welcome_message = message.text.replace("/setwelcome", "").strip()
    bot.reply_to(message, "Приветственное сообщение обновлено!")

# ==== Команда /setfollowup ====
@bot.message_handler(commands=['setfollowup'])
def set_followup(message):
    if not is_admin(message.from_user.id):
        return
    global delayed_message
    delayed_message = message.text.replace("/setfollowup", "").strip()
    bot.reply_to(message, "Отложенное сообщение обновлено!")

# ==== Команда /addadmin ====
@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    if not is_admin(message.from_user.id):
        return
    try:
        _, user_id = message.text.split()
        admin_ids.append(int(user_id))
        bot.reply_to(message, f"Пользователь {user_id} добавлен в администраторы.")
    except:
        bot.reply_to(message, "Используйте формат: /addadmin [user_id]")

# ==== Запуск бота ====
bot.polling(none_stop=True, interval=0)
