import asyncio
from datetime import datetime
import json
import os
import requests
import aiohttp
import time 
from config import headers_news,URL_NEWS


conv = lambda x: datetime.strptime(x,"%Y-%m-%d %H:%M:%S")

async def req(request:str,lang='en'):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL_NEWS,headers=headers_news, params={'q':request,'lang':lang}) as s:
            answer = await s.json()

    return answer

async def sort_dict(old_dict:dict)->dict[str,list[str,int]]:
    new_dict = list(old_dict.items()) # Преобразование словаря в список из кортежей, каждый из которых состоит из пары ключ:значение
    new_dict.sort(key = lambda i: i[1][1]) # Сортировка происходит по дате
    old_dict = {i[0]: i[1] for i in new_dict} # Преобразование списка в словарь. Проход по каждому картежу в списке

    return old_dict

async def get_text(request:str,lang='en') -> dict[str,list[str,int]]|None:
    all_news = {}
    while True:
        answer = await req(request)
        if 'message' in answer:
            await asyncio.sleep(2)
        else:
            break
    
    if answer['status'] == 'ok':
        for news in answer['articles']:
            if news['topic'] == 'finance' or news['topic'] == 'business':
                if news['title'] not in all_news:
                    day = datetime.today().date() - conv(news['published_date']).date()
                    all_news[news["title"]] = [news["link"],day.days]
    else:
        print('ПУСТО')
        return None
    
    return await sort_dict(all_news)

async def format_message(request:str,lang:str='en'):
    news_link = await get_text(request,lang)
    message = ''

    if news_link == None:
        message = f'По вашему запросу ничего не найдено'
        return message

    for k,v in news_link.items():
        if int(v[1]) == 1:
            postfix = 'день назад'
        elif int(v[1]) < 5 and  int(v[1]) > 1:
            postfix = 'дня назад'
        elif int(v[1]) < 8 and  int(v[1]) > 4:
            postfix = 'дней назад'
        else:
            postfix = 'Сегодня'

        message += str(v[1]) + " " + postfix + '\n' + f'<a href="{v[0]}">{k}</a>' + '\n\n'
        print("mes:",message)
    return message.rstrip()

if __name__ == '__main__':
     pass
