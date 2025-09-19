from typing import List
from models import Location,Event
import yaml

#config.yamlからDBのカラム名を読み込む
try:
    with open("config.yaml","r",encoding="utf-8") as f:
        CONFIG=yaml.safe_load(f)
        DB_COLUMNS=CONFIG["database_columns"]
except FileNotFoundError as e:
    print(f"config.yamlが見つからない{e}")
    exit(1)

#DBから取得したdictレコードをネストされたdict型に変換する
def convert_db_record(db_record)->Event:
    loc=Location(
        lat=db_record[DB_COLUMNS["location_lat"]],
        lon=db_record[DB_COLUMNS["location_lon"]]
        )
    event=Event(
        id=db_record[DB_COLUMNS["id"]],
        pushed_timestamp=db_record[DB_COLUMNS["pushed_timestamp"]],
        name=db_record[DB_COLUMNS["name"]],
        location=loc
    )
    return event 

#DBから取得したイベントをlistとしてまとめて返す
def get_list(db_events)->List[Event]:
    events=[]
    for db_event in db_events:
        event=convert_db_record(db_event)
        events.append(event)
    return events

