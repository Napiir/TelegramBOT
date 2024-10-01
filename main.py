import telebot
from telebot import types, TeleBot
import json

bot: TeleBot = telebot.TeleBot('7702030477:AAFcnpUCOSX72jghusV9ATim2_Z8hqxabZs')

btn0 = types.InlineKeyboardButton('Telegram разработчика', url='https://t.me/Napiir')
btn1 = types.InlineKeyboardButton('начать тест', callback_data='startQuiz')
btn2 = types.InlineKeyboardButton('лидерборд', callback_data='result')

asks = {
    'Самая большая страна?': 'Россия',
    'Столица Китая?': 'Пекин',
    'Спутник Земли?': 'Луна',
    'С помощью какой птицы раньше отправляли письма?': 'Голубь',
}

user_data = {}  #  информация о пользователях


def save_to_json(chat_id, username, score):
    data = {str(chat_id): {"username": username, "score": score}}

    try:
        with open('scores.json', 'r') as json_file:
            content = json.load(json_file)
            content.update(data)
    except (FileNotFoundError, json.JSONDecodeError):
        content = data

    with open('scores.json', 'w') as json_file:
        json.dump(content, json_file, ensure_ascii=False, indent=4)


@bot.message_handler(commands=['start'])
def main(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(btn0)
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, 'Викторина на 4 вопроса', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    bot.delete_message(callback.message.chat.id, callback.message.id)

    if callback.data == 'startQuiz':
        user_data[callback.message.chat.id] = {
            'score': 0,
            'questions': list(asks.items()),  # Список вопросов
            'current_question_index': 0,
        }
        ask_question(callback.message.chat.id)

    elif callback.data == 'result':
        bot.send_message(callback.message.chat.id, "Пока не реализовано")


def ask_question(chat_id):
    if user_data[chat_id]['current_question_index'] < len(user_data[chat_id]['questions']):
        question, correct_answer = user_data[chat_id]['questions'][user_data[chat_id]['current_question_index']]
        sent = bot.send_message(chat_id, question)
        bot.register_next_step_handler(sent, lambda message: check_answer(message, correct_answer, chat_id))
    else:
        score = user_data[chat_id]['score']
        username = bot.get_chat(chat_id).username or "Неизвестный"
        save_to_json(chat_id, username, score)
        bot.send_message(chat_id, f"Вы набрали {score} баллов.")
        del user_data[chat_id]  # Удалить данные пользователя после окончания викторины


def check_answer(message, correct_answer, chat_id):
    if message.text == correct_answer:
        bot.send_message(chat_id, 'Правильно!')
        user_data[chat_id]['score'] += 1
    else:
        bot.send_message(chat_id, 'Неверно!')

    user_data[chat_id]['current_question_index'] += 1
    ask_question(chat_id)


bot.polling(none_stop=True)