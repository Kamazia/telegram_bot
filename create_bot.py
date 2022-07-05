from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage # Хранение данных в оперативной памяти. Машина состояний
import redis
from redis_data import *
from config import TOKEN

storage = MemoryStorage()

bot = Bot(token = TOKEN)
dp = Dispatcher(bot,storage = storage)
set_data()

'''storage = MemoryStorage()
while True:
    try:
        r = redis.from_url(os.environ.get("REDIS_URL"))
        r.set('123','test')
        print(r.get('123'))
        break
    except:'''
