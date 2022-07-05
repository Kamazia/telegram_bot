from aiogram.utils import executor
from main import dp
from cashews import cache
#from create_bot import dp
 

def checking_resources():
    pass


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=checking_resources())