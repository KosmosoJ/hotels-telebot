import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('lowprice', "Поиск дешевых отелей"),
    ('highprice', "Поиск дорогих отелей"),
    ('bestdeal', "Поиск лучших отелей"),
    ('history', "Вывести последний поиск отелей"),
    ('help', "Вывести справку")   
)


CITY_URL = "https://hotels4.p.rapidapi.com/locations/v2/search"

HEADERS = {
	"X-RapidAPI-Key": RAPID_API_KEY,
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

HOTELS_URL = "https://hotels4.p.rapidapi.com/properties/v2/list"

HOTEL_URL = "https://hotels4.p.rapidapi.com/properties/v2/detail"


DB_PATH = "database\\user_search.db"