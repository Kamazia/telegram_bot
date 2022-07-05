import os
from aiogram import types
from aiogram.utils import executor
import redis
from keyboards import keyboard
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from create_bot import dp, bot
from ticker import ticker_actions
from news.get_news import format_message
from portfolio import portfolio_actions
import config
import re
r = redis.from_url(os.environ.get("REDIS_URL"),decode_responses=True)

class FSMportfolio(StatesGroup):
    add_stock = State()
    edit_stock = State()


class FSMtikers(StatesGroup):
    tickers = State()


class FSMnews(StatesGroup):
    news = State()


#-------------------------Commands--------------------------------------#

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message)-> None:
    """ Ответ на команду старт """
    #r = redis.from_url(os.environ.get("REDIS_URL"),decode_responses=True)
    await bot.send_message(
        chat_id=message.chat.id,
        text=r.get('start_message'),
        reply_markup=keyboard.down_keyboard()
    )


@dp.message_handler(commands=['help'])
async def help_message(message: types.Message)-> None:
    """ Ответ на команду help"""
    await bot.send_message(
        chat_id=message.chat.id,
        text=r.get('help_message'),
        parse_mode='HTML'
    )


@dp.message_handler(content_types=['text'], state=None)
async def text_message(message: types.Message,state: FSMContext)-> None:
    """
    Функция, которая отправляет ответ на любой текст.
    Если текст соответствует одной из следующих команд, выполяется соответствующие действие,
    если введен какой то неизвестный текст выводится сообщение об этом

    """
    if message.text.lower() == "тикер":
        await FSMtikers.tickers.set()
        message = await bot.send_message(
            chat_id=message.chat.id,
            text=r.get('tickers'),
            parse_mode='HTML',
            reply_markup=keyboard.cancel_menu()
        )
        async with state.proxy() as data:
            data['message_id'] = message

    elif message.text.lower() == "портфель":
        await bot.send_message(
            chat_id=message.chat.id,
            text=r.get('portfolio_message'),
            reply_markup=keyboard.portfolio_menu()
        )

    elif message.text.lower() == "новости":
        await FSMnews.news.set()
        await bot.send_message(
            chat_id=message.chat.id,
            text=r.get('news_message'),
            parse_mode='HTML'
        )

    elif message.text.lower() == "теория":
        await bot.send_message(
            chat_id=message.chat.id,
            text=r.get('teoria_message'),
            parse_mode='HTML',
            reply_markup=keyboard.teoria()
        )
    
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Пока я не знаю такую команду\nчтобы узнать список команд\nвведите /help"
        )


#-------------------------CallBack--------------------------------------#

@dp.callback_query_handler(lambda callback: callback.data == 'cancel',state='*')
async def cancel_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    
    if current_state is None:
        await bot.edit_message_text(
            message_id=callback_query.message.message_id,
            chat_id=callback_query.from_user.id,
            text='cancel',
        )

        return

    elif current_state == 'FSMportfolio:add_stock' or current_state =='FSMportfolio:edit_stock':
        await state.finish()
        await bot.edit_message_text(
            message_id=callback_query.message.message_id,
            chat_id=callback_query.from_user.id,
            text=r.get('portfolio_message'),
            reply_markup=keyboard.portfolio_menu()
        )

        return
    
    else:
        await state.finish()
        await bot.edit_message_text(
            message_id=callback_query.message.message_id,
            chat_id=callback_query.from_user.id,
            text='cancel',
        )
        return

@dp.callback_query_handler(lambda callback: True)
async def process_callback_button1(callback_query: types.CallbackQuery,state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    if callback_query.data == 'add':
        bot_message = await bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id ,
            text=r.get('add_in_portfolio'),
            reply_markup=keyboard.cancel_menu(),
            parse_mode='HTML'
        )
        await FSMportfolio.add_stock.set()
        async with state.proxy() as data:
            data['message_id'] = bot_message

        return

    elif callback_query.data == 'edit':
        now = await portfolio_actions.get_portfolio_info(callback_query.from_user.id)
        if now == None:
            bot_message = await bot.edit_message_text(
                chat_id=callback_query.from_user.id,
                text=f'У вас ещё нет составленного портфеля, будет создан новый',
                reply_markup=keyboard.cancel_menu(),
                message_id=callback_query.message.message_id,
            )

        else:
            answer = '\n'
            for k,v in now.items():
                if k != 'start_cost':
                    answer += f'{k} - {v}\n'

            bot_message = await bot.edit_message_text(
                chat_id=callback_query.from_user.id,
                text=f'Сейчас у вас есть {answer.rstrip()}\n\nВведите новый список тикеров, который заменит этот список или нажмите кнопку отмены',
                reply_markup=keyboard.cancel_menu(),
                message_id=callback_query.message.message_id,
            )
            
        await FSMportfolio.edit_stock.set()
        async with state.proxy() as data:
            data['message_id'] = bot_message
        return

    elif callback_query.data  == 'cost':
        info = await portfolio_actions.get_portfolio_info(callback_query.from_user.id)
        if info:
            answer_message = ''
            start_cost = info.pop('start_cost')
            keys = [*info]
            value = []

            for k,v in info.items():
                answer_message += f'{k} - {v} шт\n'
                value.append(int(v))


            portfolio_prices = await ticker_actions.get_price(keys,0) # список цен тикеров
            sum_price = sum([value[i]*portfolio_prices[i] for i in range(len(portfolio_prices))]) # сумма цен тикеров
            procent = (sum_price*100)/start_cost-100 # процент прибыли
            
            await bot.edit_message_text(
                chat_id=callback_query.from_user.id,
                text=f'Стоимость вашего портфеля {round(sum_price,1)}$\nСтоимость изменилась на {round(procent, 1)} %',
                message_id=callback_query.message.message_id,
            )

        else:
            await bot.edit_message_text(
                chat_id=callback_query.from_user.id,
                text='\U00002B55 Ваш портфель пуст \U00002B55\n\nСначала добавьте в него активы, чтобы отслеживать их стоимость',
                message_id=callback_query.message.message_id,
                reply_markup=keyboard.empty_cost()
            )


#-------------------------FSM state--------------------------------------#

@dp.message_handler(state=FSMportfolio.add_stock,content_types=['text'])
async def post_stock(message: types.Message, state: FSMContext) -> None:
    """ 
    Принимаем акции от пользователя
    """

    async with state.proxy() as data:
        old_message = data['message_id']
    await bot.delete_message(message.chat.id,old_message.message_id)
    await state.finish()

    regex = re.compile('[a-zA-Z]{1,6}/[0-9]{1,10}')
    data = regex.findall(message.text)
    
    if not data:
        bot_message = await bot.send_message(
            chat_id=message.chat.id,
            text='\U00002B55 Были введены некоректные данные \U00002B55\n\nМы не смогли добавить акции\n\nПопробуйте ввести ещё раз',
            reply_markup=keyboard.cancel_menu()
        )
        await FSMportfolio.add_stock.set()
        async with state.proxy() as data:
            data['message_id'] = bot_message

        return

    else:
        stocks = {'id':message.chat.id}

        stocks['portfolio'] = {i.split('/')[0].upper():int(i.split('/')[1]) for i in data}

        price = await ticker_actions.get_price(stocks['portfolio'].keys(),0)
        all = 0
        exception = []
        for i in range(len(price)):
            if price[i] != 'неверный тикер':
                all += int(data[i].split('/')[1])*float(price[i])
            
            elif price[i] == 'неверный тикер':
                a = [*stocks['portfolio']]
                exception.append(a[i])

        stocks['portfolio'].update({'start_cost':all})
        text = '\U0001F4BC Данные добавлены \U0001F4BC'
        if exception:
            text+=f'\n\nКроме {",".join(exception)}'
            for i in exception:
                del stocks['portfolio'][i]

        answer = await portfolio_actions.create_or_update_portfolio(stocks)
        
        await bot.send_message(
            chat_id=message.chat.id,
            text=text,
            parse_mode='HTML',
            disable_web_page_preview=True
        )


@dp.message_handler(state=FSMportfolio.edit_stock)
async def put_stock(message: types.Message, state: FSMContext) -> None:

    async with state.proxy() as data:
        old_message = data['message_id']
    await bot.delete_message(message.chat.id,old_message.message_id)
    await state.finish()

    data = message.text
    regex = re.compile('[a-zA-Z]{1,6}/[0-9]{1,10}')
    data = regex.findall(data)

    if not data:
        await bot.send_message(
            chat_id=message.chat.id,
            text='Были введены некоректные данные, мы не смогли обновить ваши акции\n\nВведите ещё раз',
            reply_markup=keyboard.cancel_menu(),

        )
        await FSMportfolio.edit_stock.set()

        return

    else:
        stocks = {}
        stocks['portfolio'] = {stock.split('/')[0].upper():int(stock.split('/')[1]) for stock in data}

        price = await ticker_actions.get_price(stocks['portfolio'].keys(),0)
        all = 0
        for i in range(len(price)):
            if price[i] != 'неверный тикер':
                all += int(data[i].split('/')[1])*float(price[i])

        stocks['portfolio'].update({'start_cost':all})

        answer = await portfolio_actions.change_portfolio_info(message.from_user.id,stocks)

        await bot.send_message(
            chat_id=message.chat.id,
            text='Портфель обновлён',
            disable_web_page_preview=True
        )


@dp.message_handler(state=FSMnews.news)
async def get_news(message: types.Message, state: FSMContext) -> None:
    """ 
    Функция принимает темы для поиска новостей,выполняет вызов фунции format_message(),
    которая возвращает форматированное сообщение и отправляет это сообщение пользователю

    """
    await state.finish()
    data = message.text

    answer = await format_message(data)
    print(answer)

    await bot.send_message(
        chat_id=message.chat.id,
        text=answer,
        parse_mode='HTML',
        disable_web_page_preview=True
    )


@dp.message_handler(state=FSMtikers.tickers)
async def get_tickers(message: types.Message, state: FSMContext)-> None:
    """ Функция обрабатывающая введеные тикеры, в ответ отправляет сообщение с ценой запрошенных акций"""

    async with state.proxy() as data:
        old_message = data['message_id']
    await bot.delete_message(message.chat.id,old_message.message_id)
    await state.finish()

    data = re.sub("[^A-Za-z .]", "", message.text).split(' ')
    data = list(filter(None, data))

    if not data:
        """Не было введено ни одной буквы"""
        old_message = await bot.send_message(
            chat_id=message.chat.id,
            text='\U00002B55 Введены некорректные данные \U00002B55\n\nПопробуйте ещё раз',
            reply_markup=keyboard.cancel_menu(),
        )
        await FSMtikers.tickers.set() 
        async with state.proxy() as data:
            data['message_id'] = old_message

        return


    elif len(data) == 1:
        """Введен один тикер"""
        message_bot = await bot.send_message(chat_id=message.chat.id, text="Тикер принят")
        graph,text = await ticker_actions.get_full_info(data)
        await bot.delete_message(message.chat.id,message_bot.message_id)
        if graph:
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=graph,
                caption=text,
            )

        else:
            message_bot = await bot.send_message(
                chat_id=message.chat.id,
                text=text,
                reply_markup=keyboard.cancel_menu(),
            )
            await FSMtikers.tickers.set() 
            async with state.proxy() as data:
                data['message_id'] = message_bot 

            return


    else:
        """Введено несколько тикеров"""
        message_bot = await bot.send_message(chat_id=message.chat.id, text="Тикеры приняты")
        answer = await ticker_actions.get_price(data)

        await bot.delete_message(message.chat.id,message_bot.message_id)
        await bot.send_message(
            chat_id=message.chat.id,
            text=answer
        ) 


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
