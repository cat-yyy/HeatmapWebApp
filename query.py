from typing import List
from models import Location,Event

def get_coordinates(events)->List:
    #タプルとしてまとめる
    coordinates_list=[(event.location.lat,event.location.lon)for event in events]
    return coordinates_list

