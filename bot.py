import sqlite3
import telebot
from telebot import types

token = '5965081035:AAGOY9lXG0IP4xmCqIbZvAifjp_4yXjvVfc'

bot = telebot.TeleBot(token)


class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def number_exists(self, number):
        """Проверяем, есть ли номер в базе"""
        result = self.cursor.execute("SELECT `id` FROM `records` WHERE `number` = ?", (number,))
        return bool(len(result.fetchall()))

    def get_spam_count(self, number):
        """Достаем spam_count номера"""
        result = self.cursor.execute("SELECT `spam_count` FROM `records` WHERE `number` = ?", (number,))
        return result.fetchone()[0]

    def add_number(self, number):
        """Добавляем номер в базу"""
        self.cursor.execute("INSERT INTO `records` (`number`) VALUES (?)", (number,))
        return self.conn.commit()

    def add_record(self, number, spam_count):
        """Создаем запись о спаме"""
        self.cursor.execute("INSERT INTO `records` (`number`, `spam_count`) VALUES (?, ?)", number, spam_count + 1)
        return self.conn.commit()

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()


database = BotDB('numbers.db')


@bot.message_handler(commands=["start"])
def welcome(message):
    # database

    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Проверить номер")
    markup.add(item1)
    bot.send_message(message.chat.id,
                     "Привет, я бот созданный чтобы очистить твои звонки от незнакомых спамеров".format(
                         message.from_user, bot.get_me()),
                     parse_mode='html', reply_markup=markup)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    if message.chat.type == 'private':
        if message.text == 'Проверить номер':
            bot.send_message(message.chat.id, 'Введи номер для проверки!')
        elif message.text == message.text:
            bot.send_message(message.chat.id, 'Проверяю')
            if database.number_exists(message.text) == True:
                bot.send_message(message.chat.id, database.get_spam_count())
            else: database.add_number(message.text)
        else:
            bot.send_message(message.chat.id, 'Я не знаю что ответить 😢')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data == 'good':
                bot.send_message(call.message.chat.id, '')
            # remove inline buttons
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="😊 Как дела?",
                                  reply_markup=None)

            # show alert
            bot.answer_callback_query(callback_query_id=call.id, show_alert=False,
                                      text="Спасибо за помощь")

if __name__ == '__main__':
    bot.infinity_polling()
