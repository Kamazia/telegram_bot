import io
import matplotlib.pyplot as plt
import pandas
from yahoo_finance_async import OHLC
from asgiref.sync import sync_to_async
from finvizfinance.quote import finvizfinance
import yfinance as yf
plt.switch_backend('agg')


async def get_graph(hist:yf.ticker.Ticker,name_company:pandas.DataFrame) -> bytes:
    """
    Создание графика из
    - исторических данных `hist` (цены по дате)
    - названия компании для легендыы
    """
    max:pandas.DataFrame = hist[hist['Close']==hist['Close'].max()]
    min:pandas.DataFrame = hist[hist['Close']==hist['Close'].min()]

    plt.plot(hist.index.values,hist['Close'])
    plt.scatter(x=max.index.values,y=max['Close'], color='g')
    plt.scatter(x=min.index.values,y=min['Close'], color='r')
    plt.title(f'График {name_company} за 1 год')
    plt.xlabel(u'Цена')
    plt.ylabel(u'Дата')
    plt.legend(('График','Max цена','Min цена'), frameon=False)

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()

    buf.seek(0)
    a = buf.getvalue()
    buf.close()

    return a


async def get_price(tickers:list,flag:bool=1) -> str|list:
    """
    Получение цен на акции
    - flag == 1 для получение форматированного сообщения с ценами
    - flag == 0 для получения списка цен
    """

    if flag:
        message = ""
        for ticker in tickers:
            try:
                result = await OHLC.fetch(symbol=ticker)
                message += f"\U00002705 {ticker} {result['meta']['regularMarketPrice']} $\n"
            except:
                message += f"\U0000274C {ticker} неверный тикер\n"

        return message.rstrip()

    else:
        price = []
        for ticker in tickers:
            try:
                result = await OHLC.fetch(symbol=ticker)
                price.append(float(result['meta']['regularMarketPrice']))
            except:
                price.append('неверный тикер')

        return price


async def format_info(fundament_stock) -> str:
    """
    Форматирование сообщения с полной инфой компании
    """
    return f"\U0001F539Компания: {fundament_stock['Company']}\n\U0001F539Сектор: {fundament_stock['Sector']}\n\U0001F539Стоимость: {fundament_stock['Price']}\n\U000025FD P/E: {fundament_stock['P/E']}\n\U000025FD P/S: {fundament_stock['P/S']}\n\U000025FD P/BV (P/B): {fundament_stock['P/B']}\n\U000025FD PEG: {fundament_stock['PEG']}\n\U000025FD P/CF(P/FCF): {fundament_stock['P/FCF']}\n\U000025FD D/E: {fundament_stock['Debt/Eq']}\n\U000025FD ROE: {fundament_stock['ROE']}\n\U000025FD Рост EPS(5л): {fundament_stock['EPS next 5Y']}"


async def key_indicators(ticker:list):
    """
    Получение ключевых показателей
    - False если не удалось получить данные
    - Список с показателями если всё окей
    """
    try:
        fundament_info = await sync_to_async(finvizfinance)(ticker[0])
    except Exception:
        return False
    
    indicators = fundament_info.ticker_fundament()

    return indicators


async def history_data(ticker:list):
    """
    Получение исторической инфо
    """
    try:
        stock = await sync_to_async(yf.Ticker)(ticker[0])
    except:
        return False

    hist = stock.history(period="1y")

    return hist


async def get_full_info(ticker:list):
    indicators = await key_indicators(ticker)

    if indicators:
        stock = await sync_to_async(yf.Ticker)(ticker[0])
        hist = stock.history(period="1y")

        graph  = await get_graph(hist,indicators['Company'])
        message = await format_info(indicators)

        return graph,message

    else:
        return False,"\U0001F614 Не удалось получить данные \U0001F614\n\nВозможно вы ввели неверный тикер, а возможно я ещё такого просто не знаю\n\nПопробуйте другой"
