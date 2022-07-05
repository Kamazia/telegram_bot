from aiogram.types import KeyboardButton,ReplyKeyboardMarkup,InlineKeyboardButton,InlineKeyboardMarkup

footer_button = [
    KeyboardButton('Тикер'),
    KeyboardButton('Портфель'),
    KeyboardButton('Новости'),
    KeyboardButton('Теория')
]

portfolio_button = [
    InlineKeyboardButton(text='Добавить', callback_data='add'),
    InlineKeyboardButton(text='Изменить', callback_data='edit'),
    InlineKeyboardButton(text='Узнать цену', callback_data='cost')
]

cancel_button = InlineKeyboardButton(text='Отмена', callback_data='cancel')

teo = [
    InlineKeyboardButton(text='Показатели', url='https://telegra.ph/Klyuchevye-pokazateli-dlya-ocenki-kompanii-07-05'),
    InlineKeyboardButton(text='Проект Банка России', url='https://fincult.info/'),
    InlineKeyboardButton(text='Интересно почитать', url='https://vashkaznachei.ru/10-ponyatiy-kotorye-nuzhno-znat-vsem-nachinajushhim-investoram/'),
    InlineKeyboardButton(text='Полезное', url='https://www.tinkoff.ru/invest/education/'),
]

def empty_cost():
    return InlineKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True).add(portfolio_button[0],cancel_button)

def down_keyboard():
    return ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True).add(*footer_button)

def portfolio_menu():
    return InlineKeyboardMarkup(row_width=3).add(*portfolio_button,cancel_button)

def cancel_menu():
    return InlineKeyboardMarkup().add(cancel_button)

def teoria():
    return InlineKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True).add(*teo)