import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from config_data import config

from peewee import *


db = SqliteDatabase(config.DB_PATH)

class BaseModel(Model):
    
    class Meta:
        database = db
        id = PrimaryKeyField(unique = True)
        order_by = 'id'
        
class UserSearch(BaseModel):
    class Meta:
        db_table = 'user_search'
        
    s_user_id = IntegerField()
    s_called_at = DateTimeField()
    s_called_command = CharField(max_length = 20)

class HotelInfo(BaseModel):
    class Meta:
        db_table = 'hotel_info'
        
    s_hotel_id = IntegerField()
    s_hotel_name = CharField(max_length = 100)
    s_hotel_address = TextField()
    s_hotel_price = IntegerField()
    s_period = IntegerField()
    s_called_from = ForeignKeyField(UserSearch, to_field = 'id')
    s_need_photo = BooleanField()
    s_distance_from_downtown = FloatField(default = 0)

class Photos(BaseModel):
    class Meta:
        db_table = 'hotel_photo'
        
    
    s_photo_hotel_id = IntegerField()
    s_photo = CharField(max_length = 300)

    
if __name__ == '__main__':
    db.create_tables([UserSearch, HotelInfo, Photos])