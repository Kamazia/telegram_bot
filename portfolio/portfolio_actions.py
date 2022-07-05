import os
import asyncio
import motor.motor_asyncio

HOST = 'localhost'
PORT = 27017

async def get_portfolio_info(user_id: str) -> dict|None:
    #db_client = motor.motor_asyncio.AsyncIOMotorClient(HOST, PORT)
    db_client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGO_URL"))
    collection = db_client.user_info.telegram_user
    portfolio_info = await collection.find_one({'id': user_id})

    if portfolio_info:
        portfolio_info.pop('_id', [None])
        return portfolio_info['portfolio']

    return None


def update_existing_student_info_with_new(existing: dict, new: dict) -> None:  # existing - существующий словарь, new - новый словарь
    for key, value in new.items():  # Проходимся по ключам и значениями нового
        if key == 'id':  # Если ключем является поле 'id' или 'email' то скипаем, потому что их нельзя менять
            continue
        
        if key == 'start_cost':
             existing[key]+=new[key]
             continue

        if key not in existing:  # Если в сущ. словаре нет ключа из нового словаря
            existing[key] = value  # то мы добавлям сущ. словарь эти данные
            continue

        if not isinstance(existing[key], dict):  # Если ключ существующего словаря НЕ словарь
            existing[key] = value  # то мы добавляем в него значение
            continue

        if not isinstance(value, dict):  # Если значение не словарь
            existing[key] = value  # то добавляем значение
            continue


        update_existing_student_info_with_new(existing[key], value)  # Если значение словарь


async def update_portfolio(existing: dict, new: dict):
    for key, value in new['portfolio'].items():
        if key == 'start_cost':
            existing['portfolio'][key] = float(existing['portfolio'][key])+float(value)
            continue

        elif key not in existing['portfolio']:
            existing['portfolio'][key] = value

        elif key in existing['portfolio']:
            existing['portfolio'][key] = int(existing['portfolio'][key])+int(value)

    return existing


async def create_or_update_portfolio(student_information: dict) -> dict:
    user_id = student_information['id']
    db_client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGO_URL"))
    #db_client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGO_URL"))
    collection = db_client.user_info.telegram_user

    existing_student_information = await collection.find_one({'id': user_id})

    if not existing_student_information:
        collection.insert_one(student_information)

        student_information.pop('_id', [None])

        return student_information

    existing_student_information = await update_portfolio(existing_student_information, student_information)

    collection.replace_one({'id': user_id}, existing_student_information)
    existing_student_information.pop('_id', [None])

    return existing_student_information


async def change_portfolio_info(user_id:str,new:dict):
    db_client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGO_URL"))
    collection = db_client.user_info.telegram_user
    portfolio_info = await collection.find_one({'id': user_id})
    new['id'] = user_id
    if portfolio_info:
        collection.replace_one({'id': user_id}, new)
        
    else:
        collection.insert_one(new)
    


if __name__ == '__main__':
    pass