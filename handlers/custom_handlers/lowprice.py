import requests
import json
from loader import bot
from telebot.types import Message, InputMediaPhoto
from states.hotel_user_info import UserHotelInfo
from config_data import config
from datetime import datetime, timedelta
from peewee import *
from database.create_tables import *
from . import calendar_get_dates



@bot.message_handler(commands=['lowprice'])
def lowprice(message:Message) -> None:
    """Приглашение пользователя на ввод города"""
    
    try:
        check_db = UserSearch.select().get_or_none()
        bot.set_state(message.from_user.id, UserHotelInfo.l_city,message.chat.id) 
        bot.send_message(message.from_user.id,f'{message.from_user.username},\nвведите город для поиска дешевых отелей (на русском языке)')
        
        with bot.retrieve_data(message.from_user.id,message.chat.id) as data: 
            data['time'+str(message.chat.id)] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
    except Exception:
        print('База данных не создана. Запустите скрипт "create_tables.py"')
        

    
        

@bot.message_handler(state = UserHotelInfo.l_city)
def get_city(message:Message) -> None:
    """Обработка введенного пользователем города"""    
    
    city_querystring = {"query":f"{message.text}","locale":"ru_RU","currency":"EUR"}
    
    if message.text.isalpha():
        bot.send_message(message.from_user.id, 'Поиск города...')
        city_response = requests.request("GET", config.CITY_URL, headers=config.HEADERS, params=city_querystring).json()
        
        if len(city_response['suggestions'][0]['entities']) == 0:
            bot.send_message(message.from_user.id, 'Неверно введен город.')
            bot.set_state(message.from_user.id, None, message.chat.id)
            
        else:
            
            try:
                user_city_id = city_response['suggestions'][2]['entities'][0]['geoId']
            except IndexError:
                user_city_id = city_response['suggestions'][0]['entities'][0]['geoId']
            
            bot.set_state(message.from_user.id, UserHotelInfo.l_dates, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                
                data['city'+str(message.chat.id)] = message.text
                data['user_city_id'+str(message.chat.id)] = user_city_id
                
            get_check_in(message)
    else:
        bot.send_message(message.from_user.id, 'Неверно указан город.')


def get_check_in(message: Message) -> None:
    """Запрос даты заселения. Основной код прописан в calendar_get_dates.py"""
    
    bot.set_state(message.from_user.id, UserHotelInfo.l_check_out, message.chat.id)

    calendar_get_dates.user_calendar_one(message)


@bot.message_handler(state = UserHotelInfo.l_check_out)
def get_check_out(message:Message) -> None:
    """Запрос срока проживания в номере"""
    
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:   
            if int(message.text) > 0:
                check_in = data['check_in'+str(message.chat.id)]
                
                if int(message.text) > 60:
                    check_out = datetime.strptime(check_in, '%Y-%m-%d').date() + timedelta(days=60)
                    
                elif int(message.text) <= 60:
                    check_out = datetime.strptime(check_in, '%Y-%m-%d').date() + timedelta(days=int(message.text))
                    
                data['check_out'+str(message.chat.id)] = check_out
                data['period'+str(message.chat.id)] = int(message.text)
                
                bot.send_message(message.from_user.id, 'Сколько отелей вывести? (максимум 10)')
                bot.set_state(message.from_user.id, UserHotelInfo.l_img_of_hotel, message.chat.id)
                
            else:
                bot.send_message(message.from_user.id, 'Нельзя забронировать меньше чем на 1 день.')
                bot.set_state(message.from_user.id, None, message.chat.id)
                
    else:
        bot.send_message(message.from_user.id, 'Не знаю, что вы хотели этим сказать.')
        bot.set_state(message.from_user.id, None, message.chat.id)
                
    
@bot.message_handler(state = UserHotelInfo.l_img_of_hotel)
def get_img_of_hotel(message: Message) -> None:
    """Обработка срока проживания. Уточняем нужны ли фотографии"""
    
    if message.text.isalpha():
        bot.send_message(message.from_user.id,'Нужно ввести число!')
        bot.set_state(message.from_user.id, None, message.chat.id)
        
    else:
        bot.set_state(message.from_user.id, UserHotelInfo.l_how_many_img, message.chat.id)
        bot.send_message(message.from_user.id, 'Вывести изображения отелей? (да/нет)')
        
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            
            if int(message.text) > 10:
                data['hotel_amt'+str(message.chat.id)] = 10
                
            else:
                data['hotel_amt'+str(message.chat.id)] = int(message.text)
            
            
@bot.message_handler(state = UserHotelInfo.l_how_many_img)
def get_amt_of_hotel_img(message:Message) -> None:
    """Обработка ответа пользователя по фотографиям. В случае положительного ответа - запрос кол-ва фоторографий"""

    if message.text.isalpha():
        if message.text.lower() == 'да':
            bot.send_message(message.from_user.id, 'Сколько фотографий вывести? (Максимум 4)')
            
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['hotel_img'+str(message.chat.id)] = 'yes'
                
            bot.set_state(message.from_user.id, UserHotelInfo.l_get_hotel, message.chat.id)
            
        elif message.text.lower() == 'нет':
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['hotel_img'+str(message.chat.id)] = 'no'
            send_hotels(message)
            
    else:
        bot.send_message(message.from_user.id, 'Не знаю, что вы хотели этим сказать.')
        bot.set_state(message.from_user.id, None, message.chat.id)
        
@bot.message_handler(state = UserHotelInfo.l_get_hotel)
def get_last_info(message:Message) -> None:
    """Обработка кол-ва фотографий"""
    
    if message.text.isalpha():
        bot.send_message(message.from_user.id, 'Нужно ввести число!')
        bot.set_state(message.from_user.id, None, message.chat.id)
        
    else:
        if int(message.text) > 4:
            img_amt = 4
        else:
            img_amt = int(message.text)
            
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['hotel_img_amt'+str(message.chat.id)] = img_amt
                
        send_hotels(message)
        

def send_hotels(message: Message):
    """Запрос к апи с выводом найденных отелей пользователю. Также запись информации в базу данных."""
    bot.set_state(message.from_user.id, None, message.chat.id)
    bot.send_message(message.from_user.id,'Ищу отели...')
    
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:

        check_in = str(data['check_in'+str(message.chat.id)])
        check_in = check_in.split('-')
        check_out = str(data['check_out'+str(message.chat.id)])
        check_out = check_out.split('-')
        
        holtel_payload = {
	"currency": "EUR",
	"eapid": 1,
	"locale": "ru_RU",
	"siteId": 300000001,
	"destination": {"regionId": data['user_city_id'+str(message.chat.id)]},
	"checkInDate": {
		"day": int(check_in[2]),
		"month": int(check_in[1]),
		"year": int(check_in[0])
	},
	"checkOutDate": {
		"day": int(check_out[2]),
		"month": int(check_out[1]),
		"year": int(check_out[0])
	},
	"rooms": [
		{
			"adults": 2,
			"children": [{"age": 5}, {"age": 7}]
		}
	],
	"resultsStartingIndex": 0,
	"resultsSize": data['hotel_amt'+str(message.chat.id)],
	"sort": "PRICE_LOW_TO_HIGH",
	"filters": {"price": {
			"max": 400,
			"min": 20
		}}
        }
        
        error = 0
        sended_hotels = 0
        
        hotels_response = requests.request("POST", config.HOTELS_URL, json=holtel_payload, headers=config.HEADERS).json()
        
        UserSearch(
                    s_user_id = message.chat.id,
                    s_called_at = data['time'+str(message.chat.id)],
                    s_called_command = 'lowprice'
                    
                    ).save()    
        
        try:
            for hotel in range(0,data['hotel_amt'+str(message.chat.id)]):
                
                hotel_name = hotels_response['data']['propertySearch']['properties'][hotel]['name']
                hotel_id = hotels_response['data']['propertySearch']['properties'][hotel]['id']
                
                hotel_find_sample = {
                    "currency": "EUR",
                    "eapid": 1,
                    "locale": "ru_RU",
                    "siteId": 300000001,
                    "propertyId": hotel_id
                    }
                
                hotel_info = requests.request("POST", config.HOTEL_URL, json=hotel_find_sample, headers=config.HEADERS).json()
                hotel_adress = hotel_info['data']['propertyInfo']['summary']['location']['address']['addressLine']
                hotel_price = round(int(hotels_response['data']['propertySearch']['properties'][hotel]['price']['lead']['amount']),2)
                
                if data['hotel_img'+str(message.chat.id)] == 'yes':
                    
                    hotel_imgs = []
                    for photo in range(data['hotel_img_amt'+str(message.chat.id)]):
                        
                        hotel_imgs.append(hotel_info['data']['propertyInfo']['propertyGallery']['images'][photo]['image']['url'])
                        
                    media_group = []
                    
                    for url in hotel_imgs:
                        media_group.append(InputMediaPhoto(media = url))

                if data['hotel_img'+str(message.chat.id)] == 'yes':
                    text_sample = f'Отель: {hotel_name}\nАдрес: {hotel_adress}\nЦена: {hotel_price}€\nОбщая цена за {data["period"+str(message.chat.id)]}дн.: {hotel_price * data["period"+str(message.chat.id)]}€\nФото отеля:'
                    bot.send_message(message.chat.id, text_sample)
                    bot.send_media_group(message.chat.id, media_group)
                    
                    sended_hotels += 1
                    
                else:
                    text_sample = f'Отель: {hotel_name}\nАдрес: {hotel_adress}\nЦена: {hotel_price}€\nОбщая цена за {data["period"+str(message.chat.id)]}дн.: {hotel_price * data["period"+str(message.chat.id)]}€'
                    bot.send_message(message.chat.id, text_sample)
                    
                    sended_hotels += 1
                
                
                if data['hotel_img'+str(message.chat.id)] == 'yes':
                    HotelInfo(
                    s_hotel_id = hotel_id,
                    s_hotel_name = hotel_name,
                    s_hotel_address = hotel_adress,
                    s_hotel_price = hotel_price,
                    s_period = data["period"+str(message.chat.id)],
                    s_called_from = UserSearch.select().where(UserSearch.id).order_by(UserSearch.s_called_at.desc()).get(),
                    s_need_photo = True
                    ).save()    
                    
                else:
                    HotelInfo(
                    s_hotel_id = hotel_id,
                    s_hotel_name = hotel_name,
                    s_hotel_address = hotel_adress,
                    s_hotel_price = hotel_price,
                    s_period = data["period"+str(message.chat.id)],
                    s_called_from = UserSearch.select().where(UserSearch.id).order_by(UserSearch.s_called_at.desc()).get(),
                    s_need_photo = False
                    ).save()
                
                
                if data['hotel_img'+str(message.chat.id)] == 'yes':
                    for url in hotel_imgs:
                        if Photos.select().where(Photos.s_photo == url).get_or_none() == None:
                            Photos(
                                s_photo = url,
                                s_photo_hotel_id = hotel_id
                                
                                ).save()   
                            
                        else:
                            continue
                    
        except IndexError:
            bot.send_message(message.from_user.id, 'Это все найденные отели по вашему запросу.')
            error += 1
            
        if sended_hotels == 0:
            bot.send_message(message.from_user.id, 'Ничего не нашлось.')
        elif error == 0:
            bot.send_message(message.from_user.id, 'Это все найденные отели по вашему запросу.')