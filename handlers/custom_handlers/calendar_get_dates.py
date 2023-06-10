import datetime 
from loader import bot
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from states.hotel_user_info import UserHotelInfo

def user_calendar_one(message):
    
    calendar, step = DetailedTelegramCalendar(min_date = datetime.date.today(), calendar_id = 1, locale = 'ru').build()
    
    bot.send_message(message.chat.id, f'Введите {LSTEP[step]}', reply_markup=calendar )
    
@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def check_date_one(c):
    result,key,step = DetailedTelegramCalendar(calendar_id=1,locale = 'ru', min_date = datetime.date.today()).process(c.data)
    
    if not result and key:
        bot.edit_message_text(f'Введите {LSTEP[step]}',c.message.chat.id,c.message.message_id, reply_markup=key )
        
    elif result:
        
        bot.delete_message(c.message.chat.id,c.message.message_id)

        bot.send_message(c.message.chat.id, 'На какое кол-во дней бронируете отель? (максимально 60 дней.)')
        
        if result is not None:
            
            with bot.retrieve_data(c.message.chat.id, c.message.chat.id) as data:   
                data['check_in'+str(c.message.chat.id)] = result.strftime('%Y-%m-%d')
                

