from loader import bot
from telebot.types import Message, InputMediaPhoto
from states.hotel_user_info import UserHotelInfo
from config_data import config
from peewee import *
from database.create_tables import *
import time




@bot.message_handler(commands=['history'])
def get_history(message:Message):
    """Запрос к sql базе 'user_search.db'. Выводит последнюю вызванную пользователем команду"""
    try:
        user_query = UserSearch.select().where(UserSearch.s_user_id == message.from_user.id).order_by(UserSearch.s_called_at.desc()).get_or_none()
    except Exception:
        bot.send_message(message.from_user.id, 'Вы еще не искали отели.')
        return
    if user_query is not None:
        
        user_hotel = HotelInfo.select()

        
        bot.send_message(message.from_user.id, f'Вами была вызвана команда {user_query.s_called_command} в {user_query.s_called_at}')
        
        if user_query.s_called_command == 'lowprice' or user_query.s_called_command == 'highprice': 
            for user in user_hotel:
                if user.s_called_from_id == user_query.id:
                    
                    if user.s_need_photo == 1:
                        media_group = []
                        
                        
                        for hotel_photo in Photos.select():

                            if hotel_photo.s_photo_hotel_id == user.s_hotel_id:
                                url = hotel_photo.s_photo
                                
                                media_group.append(InputMediaPhoto(media = url))

                            else:
                                continue
                        
                        text_sample = f'Отель: {user.s_hotel_name}\nАдрес: {user.s_hotel_address}\nЦена: {user.s_hotel_price}€\nОбщая цена за {user.s_period}: {user.s_hotel_price * user.s_period}€\nФото отеля:'
                        bot.send_message(message.chat.id, text_sample)
                        bot.send_media_group(message.chat.id, media_group)
                        time.sleep(1)
                    else:
                        text_sample = f'Отель: {user.s_hotel_name}\nАдрес: {user.s_hotel_address}\nЦена: {user.s_hotel_price}€\nОбщая цена за {user.s_period}: {user.s_hotel_price * user.s_period}€'
                        bot.send_message(message.chat.id, text_sample)
                        time.sleep(1)
        elif user_query.s_called_command == 'bestdeal':
             for user in user_hotel:
                if user.s_called_from_id == user_query.id:
                    
                    if user.s_need_photo == 1:
                        media_group = []
                        
                        
                        for hotel_photo in Photos.select():

                            if hotel_photo.s_photo_hotel_id == user.s_hotel_id:
                                url = hotel_photo.s_photo
                                
                                media_group.append(InputMediaPhoto(media = url))

                            else:
                                continue
                        
                        text_sample = f'Отель: {user.s_hotel_name}\nАдрес: {user.s_hotel_address}\nЦена: {user.s_hotel_price}€\nОбщая цена за {user.s_period}: {user.s_hotel_price * user.s_period}€\nРасстояние до центра: {user.s_distance_from_downtown}миль.\nФото отеля:'
                        bot.send_message(message.chat.id, text_sample)
                        bot.send_media_group(message.chat.id, media_group)
                        time.sleep(1)
                    else:
                        text_sample = f'Отель: {user.s_hotel_name}\nАдрес: {user.s_hotel_address}\nЦена: {user.s_hotel_price}€\nОбщая цена за {user.s_period}: {user.s_hotel_price * user.s_period}€\nРасстояние до центра: {user.s_distance_from_downtown}миль.'
                        bot.send_message(message.chat.id, text_sample)
                        time.sleep(1)
    else:
        bot.send_message(message.from_user.id, 'Вы еще не искали отели.')