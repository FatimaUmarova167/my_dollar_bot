import os
import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Пытаемся загрузить .env только если файл существует
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Если библиотека python-dotenv не установлена — просто игнорируем
    pass

# Токен берётся из переменной окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Проверка: если токен не найден — выводим понятную ошибку
if TOKEN is None:
    raise ValueError("❌ Токен не найден! Создайте файл .env с TELEGRAM_TOKEN или добавьте переменную окружения.")

# Инициализируем бота
bot = telebot.TeleBot(TOKEN)


# Функция для получения курса валют
def get_exchange_rates():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    try:
        response = requests.get(url)
        data = response.json()
        usd_rate = data["Valute"]["USD"]["Value"]
        eur_rate = data["Valute"]["EUR"]["Value"]
        return {
            "usd": usd_rate,
            "eur": eur_rate
        }
    except Exception as e:
        return None


# Форматируем красивый ответ с курсами
def format_rate_message(rates):
    if rates is None:
        return "❌ Не удалось получить курс валют. Попробуйте позже!"

    text = f"""💰 <b>Актуальные курсы валют</b> 💰

🇺🇸 <b>Доллар США (USD):</b> <code>{rates['usd']:.2f} ₽</code>
🇪🇺 <b>Евро (EUR):</b> <code>{rates['eur']:.2f} ₽</code>

📅 Данные ЦБ РФ на сегодня
🔄 Обновление: ежедневно в 11:00 МСК
    """
    return text


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=2)
    btn_rate = InlineKeyboardButton("💵 Курс валют", callback_data="rate")
    btn_help = InlineKeyboardButton("❓ Помощь", callback_data="help")
    btn_about = InlineKeyboardButton("ℹ️ О боте", callback_data="about")
    markup.add(btn_rate, btn_help, btn_about)

    welcome_text = f"""👋 <b>Добро пожаловать, {message.from_user.first_name}!</b>

Я бот для получения актуальных курсов валют.

✨ <b>Мои возможности:</b>
• Отображение курса USD и EUR
• Удобное меню с кнопками
• Мгновенные ответы

📌 <b>Доступные команды:</b>
/start - Главное меню
/dollar - Курс валют
/help - Помощь
/about - Информация о боте

Или просто нажмите на кнопку ниже 👇
    """

    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="HTML",
        reply_markup=markup
    )


# Обработчик команды /dollar
@bot.message_handler(commands=['dollar'])
def send_dollar(message):
    rates = get_exchange_rates()
    text = format_rate_message(rates)
    bot.send_message(message.chat.id, text, parse_mode="HTML")


# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """❓ <b>Помощь по боту</b>

📌 <b>Доступные команды:</b>
/start - Показать главное меню
/dollar - Узнать курс валют
/help - Открыть справку
/about - Информация о боте

📌 <b>Как пользоваться:</b>
Нажмите на кнопку "Курс валют" или отправьте команду /dollar.
Бот покажет актуальный курс доллара и евро.

📌 <b>Источник данных:</b>
Центральный банк Российской Федерации

📌 <b>Время обновления:</b>
Ежедневно в 11:00 по московскому времени
    """
    bot.send_message(message.chat.id, help_text, parse_mode="HTML")


# Обработчик команды /about
@bot.message_handler(commands=['about'])
def send_about(message):
    about_text = """ℹ️ <b>О боте</b>

🤖 Данный бот предназначен для быстрого получения актуальных курсов валют.

⚙️ <b>Техническая информация:</b>
• Язык: Python 3
• Библиотеки: pyTelegramBotAPI, Requests
• Источник: API ЦБ РФ

💡 <b>Особенности:</b>
• Интуитивно понятный интерфейс
• Поддержка USD и EUR
• Быстрые ответы

📱 <b>Разработчик:</b>
@FatmaUmrva
    """
    bot.send_message(message.chat.id, about_text, parse_mode="HTML")


# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "rate":
        rates = get_exchange_rates()
        text = format_rate_message(rates)
        bot.send_message(call.message.chat.id, text, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif call.data == "help":
        help_text = """❓ <b>Быстрая справка</b>

Отправьте /help для полной инструкции.
Или нажмите /dollar, чтобы узнать курс!"""
        bot.send_message(call.message.chat.id, help_text, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif call.data == "about":
        about_text = """🤖 Бот разработан для удобного получения курсов валют.

📊 Используются официальные данные ЦБ РФ.
    """
        bot.send_message(call.message.chat.id, about_text, parse_mode="HTML")
        bot.answer_callback_query(call.id)


# Обработчик любых других сообщений
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    markup = InlineKeyboardMarkup(row_width=2)
    btn_rate = InlineKeyboardButton("💵 Курс валют", callback_data="rate")
    btn_help = InlineKeyboardButton("❓ Помощь", callback_data="help")
    markup.add(btn_rate, btn_help)

    bot.send_message(
        message.chat.id,
        "🤔 Я не понимаю эту команду.\n\nПожалуйста, используйте кнопки ниже или отправьте /help для получения справки.",
        reply_markup=markup
    )


# Запуск бота
if __name__ == "__main__":
    print("🚀 Бот успешно запущен и готов к работе!")
    print("📊 Отправьте команду /dollar в Telegram для проверки")
    bot.infinity_polling()