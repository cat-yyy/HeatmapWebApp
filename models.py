from pydantic import BaseModel
from datetime import datetime


# 位置データ
class Location(BaseModel):
    lat: float  # 緯度
    lon: float  # 経度


# PythonでJSONを扱うためのモデル
class Event(BaseModel):
    id: str
    pushed_timestamp: datetime
    name: str
    location: Location
