import telebot
import random
import json
from dotenv import load_dotenv
import os

# .env
load_dotenv()
TOKEN=os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Schedule
SCHEDULE_FILE="schedule.json"
if not os.path.exists(SCHEDULE_FILE):
    with open(SCHEDULE_FILE, "w") as f:
        json.dump({}, f)

# Start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Здраствуй! Я учебный бот-утилита. Вот что я могу:\n\n"
        "/convert - конвертация чисел\n"
        "/random - генерация случайного числа или пароля\n"
        "/schedule - управление расписанием\n"
    )

# Converting
@bot.message_handler(commands=["convert"])
def convert(message):
    bot.send_message(
        message.chat.id,
        "Напиши число для конвертации. Например:\n"
        "`10 bin` - из десятичной в двоичную\n"
        "`1010 dec` - из двоичной в десятичную",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(message, handle_conversion)

def handle_conversion(message):
    try:
        text=message.text.split()
        num, system = text[0], text[1].lower()
        if system == "bin":
            result = bin(int(num))[2:]
        elif system == "dec":
            result = int(num, 2)
        else:
            raise ValueError("Неверная система счисления")
        bot.send_message(message.chat.id, f"Результат: {result}")
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка! Убедись, что ты ввел корректные данные.")

# Random number/password
@bot.message_handler(func=lambda message: message.text.startswith("/random"))
def random_handler(message):
    command_parts = message.text.split()

    if len(command_parts) == 1:
        bot.send_message(
            message.chat.id,
            "Выбери действие:\n"
            "`/random number` — случайное число\n"
            "`/random password` — случайный пароль",
            parse_mode="Markdown"
        )
    elif len(command_parts) > 1:
        subcommand = command_parts[1].lower()
        if subcommand == "number":
            num = random.randint(1, 100)
            bot.send_message(message.chat.id, f"Случайное число: {num}")
        elif subcommand == "password":
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
            password = "".join(random.choice(chars) for _ in range(10))
            bot.send_message(message.chat.id, f"Случайный пароль: {password}")
        else:
            bot.send_message(message.chat.id, "Неизвестная подкоманда. Используй /random number или /random password.")
# Schedule
@bot.message_handler(func=lambda message: message.text.startswith("/schedule"))
def schedule_handler(message):
    command_parts = message.text.split()
    if len(command_parts) == 1:
        bot.send_message(
            message.chat.id,
            "Что ты хочешь сделать?\n"
            "`/schedule add` — добавить лекцию\n"
            "`/schedule view` — посмотреть расписание\n"
            "`/schedule delete` — удалить лекцию",
            parse_mode="Markdown"
        )
    elif len(command_parts) > 1:
        subcommand = command_parts[1].lower()
        if subcommand == "add":
            bot.send_message(message.chat.id, "Напиши название лекции и время. Например:\n`Математика, 10:00`", parse_mode="Markdown")
            bot.register_next_step_handler(message, handle_schedule_add)
        elif subcommand == "view":
            handle_schedule_view(message)
        elif subcommand == "delete":
            bot.send_message(message.chat.id, "Напиши название лекции для удаления.")
            bot.register_next_step_handler(message, handle_schedule_delete)
        else:
            bot.send_message(message.chat.id,
                             "Неизвестная подкоманда. Используй /schedule add, /schedule view или /schedule delete.")
def handle_schedule_add(message):
    try:
        text = message.text
        with open(SCHEDULE_FILE, "r") as f:
            schedule = json.load(f)
        day = "Сегодня"  # Можно добавить выбор дня
        if day not in schedule:
            schedule[day] = []
        schedule[day].append(text)
        with open(SCHEDULE_FILE, "w") as f:
            json.dump(schedule, f)
        bot.send_message(message.chat.id, "Лекция добавлена!")
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при добавлении лекции.")
def handle_schedule_view(message):
    try:
        with open(SCHEDULE_FILE, "r") as f:
            schedule = json.load(f)
        day = "Сегодня"  # Можно добавить выбор дня
        if day in schedule:
            lectures = "\n".join(schedule[day])
            bot.send_message(message.chat.id, f"Расписание на сегодня:\n{lectures}")
        else:
            bot.send_message(message.chat.id, "Расписание пустое.")
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при просмотре расписания.")
def handle_schedule_delete(message):
    try:
        lecture = message.text
        with open(SCHEDULE_FILE, "r") as f:
            schedule = json.load(f)
        day = "Сегодня"  # Можно добавить выбор дня
        if day in schedule and lecture in schedule[day]:
            schedule[day].remove(lecture)
            with open(SCHEDULE_FILE, "w") as f:
                json.dump(schedule, f)
            bot.send_message(message.chat.id, "Лекция удалена!")
        else:
            bot.send_message(message.chat.id, "Лекция не найдена.")
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при удалении лекции.")


bot.polling(none_stop=False)