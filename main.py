import telebot
from telebot import types
from config import *
from utils import APIError, CurrencyConverter
import traceback

bot = telebot.TeleBot(TOKEN)

def currencyPairs_list_updater(currencyPair):
    global currencyPairs_list
    if currencyPair in currencyPairs_list:
        currencyPairs_list.remove(currencyPair)
        currencyPairs_list = [currencyPair] + currencyPairs_list
    else:
        currencyPairs_list.pop()
        currencyPairs_list = [currencyPair] + currencyPairs_list

def create_currencyPairs_keyboard():
    row = []
    currencyPairs_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for i, currencyPair in enumerate(currencyPairs_list):
        row.append(types.KeyboardButton(currencyPair))
        count = i + 1
        if count % 3 == 0:
            currencyPairs_keyboard.row(*row)
            row = []
    return currencyPairs_keyboard

@bot.message_handler(commands=['start', 'help'])
def start_help(message):
    command = message.text
    if command == '/start':
        text = greetings_text + '\n\n' + help_text
    else:
        text = 'Вот помощь по работе со мной.' + '\n\n' + help_text
    bot.send_message(message.chat.id, text, reply_markup=create_currencyPairs_keyboard())

@bot.message_handler(commands=['currencies'])
def values(message):
    text = 'Обмен производится среди следующих валют:\n'
    for key, value in currencies_dict.items():
        text = '\n'.join((text, f'{key}: {value}'))
    bot.reply_to(message, text)

@bot.message_handler(content_types=['text'])
def request_parser(message):
    api_params = message.text.split()
    if len(api_params) == 1:
        bot.reply_to(message, f'Запрос не может состоять из одного параметра, сделайте повторный ввод', reply_markup=create_currencyPairs_keyboard())
    elif len(api_params) == 2:
        bot.reply_to(message, f'Введите обмениваемую сумму')
        bot.register_next_step_handler(message, amount_handler, api_params)
    else:
        converter(message, api_params)

def amount_handler(message, api_params):
    amount = message.text.strip()
    if len(amount.split()) != 1 or not amount.replace(',', '.').replace('.', '').isnumeric():
        bot.reply_to(message, f'Некорректное значение, сделайте повторный ввод обмениваемой суммы')
        bot.register_next_step_handler(message, amount_handler, api_params)
    else:
        api_params.append(amount)
        converter(message, api_params)

def converter(message, api_params):
    try:
        from_, to_, amount, result = CurrencyConverter.convert(api_params)
        currencyPairs_list_updater(' '.join([from_, to_]))
    except APIError as e:
        bot.reply_to(message, f'Ошибка в запросе: {str(e)}')
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        bot.reply_to(message, f"Неизвестная ошибка: {str(e)}")
    else:
        bot.reply_to(message, f"Стоимость {amount} {from_} составляет {round(result, 2)} {to_} по текущему курсу.", reply_markup=create_currencyPairs_keyboard())

bot.polling()



