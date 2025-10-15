from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import datetime

# Токен бота
BOT_TOKEN = ""

# Состояния для ConversationHandler
MAIN_MENU, SEARCH_BY_DATE, SEARCH_BY_USER, ENTER_DATE, ENTER_USERNAME = range(5)

# "База данных" сообщений (в реальном боте нужно использовать настоящую БД)
messages_db = [
    {"user": "user1", "text": "Привет всем!", "date": "2024-01-15"},
    {"user": "user2", "text": "Как дела?", "date": "2024-01-16"},
    {"user": "user1", "text": "Все отлично!", "date": "2024-01-16"},
    {"user": "user3", "text": "Погода хорошая", "date": "2024-01-17"},
]

# Главное меню
def get_main_menu():
    keyboard = [
        [KeyboardButton("🔍 Поиск по дате"), KeyboardButton("👤 Поиск по пользователю")],
        [KeyboardButton("❓ Помощь"), KeyboardButton("🚪 Выход")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Добро пожаловать в бот для поиска сообщений!\n"
        "Выберите действие в меню ниже:",
        reply_markup=get_main_menu()
    )
    return MAIN_MENU

# Обработка главного меню
async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text
    
    if user_choice == "🔍 Поиск по дате":
        await update.message.reply_text(
            "📅 Введите дату в формате ГГГГ-ММ-ДД:\n"
            "Например: 2024-01-16"
        )
        return ENTER_DATE
        
    elif user_choice == "👤 Поиск по пользователю":
        await update.message.reply_text(
            "👤 Введите имя пользователя:\n"
            "Например: user1"
        )
        return ENTER_USERNAME
        
    elif user_choice == "❓ Помощь":
        await update.message.reply_text(
            "📋 <b>Инструкция по использованию:</b>\n\n"
            "🔍 <b>Поиск по дате</b> - найти все сообщения за определенную дату\n"
            "👤 <b>Поиск по пользователю</b> - найти все сообщения конкретного пользователя\n\n"
            "💡 <b>Примеры:</b>\n"
            "Дата: 2024-01-16\n"
            "Пользователь: user1",
            parse_mode='HTML'
        )
        return MAIN_MENU
        
    elif user_choice == "🚪 Выход":
        await update.message.reply_text(
            "До свидания! Чтобы начать заново, отправьте /start",
            reply_markup=None
        )
        return ConversationHandler.END

# Поиск по дате
async def search_by_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_input = update.message.text
    
    try:
        # Проверяем правильность формата даты
        datetime.datetime.strptime(date_input, '%Y-%m-%d')
        
        # Ищем сообщения по дате
        found_messages = [msg for msg in messages_db if msg["date"] == date_input]
        
        if found_messages:
            result_text = f"📅 <b>Сообщения за {date_input}:</b>\n\n"
            for i, msg in enumerate(found_messages, 1):
                result_text += f"{i}. 👤 <b>{msg['user']}</b>: {msg['text']}\n"
        else:
            result_text = f"❌ Сообщений за {date_input} не найдено"
            
        await update.message.reply_text(result_text, parse_mode='HTML')
        
    except ValueError:
        await update.message.reply_text(
            "❌ Неправильный формат даты!\n"
            "Используйте формат: ГГГГ-ММ-ДД\n"
            "Например: 2024-01-16"
        )
        return ENTER_DATE
    
    await update.message.reply_text("Выберите следующее действие:", reply_markup=get_main_menu())
    return MAIN_MENU

# Поиск по пользователю
async def search_by_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text
    
    # Ищем сообщения по пользователю
    found_messages = [msg for msg in messages_db if msg["user"] == username]
    
    if found_messages:
        result_text = f"👤 <b>Сообщения пользователя {username}:</b>\n\n"
        for i, msg in enumerate(found_messages, 1):
            result_text += f"{i}. 📅 {msg['date']}: {msg['text']}\n"
    else:
        result_text = f"❌ Сообщений пользователя {username} не найдено"
        
    await update.message.reply_text(result_text, parse_mode='HTML')
    await update.message.reply_text("Выберите следующее действие:", reply_markup=get_main_menu())
    return MAIN_MENU

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Операция отменена. Для начала работы отправьте /start",
        reply_markup=None
    )
    return ConversationHandler.END

# Главная функция
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Настройка ConversationHandler для управления состояниями
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_main_menu)
            ],
            ENTER_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_by_date)
            ],
            ENTER_USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_by_user)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()