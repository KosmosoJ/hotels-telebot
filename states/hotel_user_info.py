from telebot.handler_backends import State, StatesGroup


class UserHotelInfo(StatesGroup):
    l_city = State()
    l_price = State()
    l_num_of_hotels = State()
    l_img_of_hotel = State()
    l_how_many_img = State()
    l_dates = State()
    l_get_hotel = State()
    l_check_out = State()

    h_city = State()
    h_price = State()
    h_num_of_hotels = State()
    h_img_of_hotel = State()
    h_how_many_img = State()
    h_dates = State()
    h_get_hotel = State()
    h_check_out = State()
    
    b_distance_from_downtown = State()
    b_city = State()
    b_price = State()
    b_num_of_hotels = State()
    b_img_of_hotel = State()
    b_how_many_img = State()
    b_dates = State()
    b_get_hotel = State()
    b_check_out = State()