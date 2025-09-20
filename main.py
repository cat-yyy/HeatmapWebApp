from fastapi import FastAPI,Request
from models import Event,Location
from typing import List,Optional
import asyncio
from dao import EventDAO
from dict_converter import get_list
import json
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from app_state import AppState

app=FastAPI()


#静的ファイルの公開
app.mount("/static",StaticFiles(directory="static"),name="static")

# templatesフォルダにあるHTMLファイルを使用
templates = Jinja2Templates(directory="static")

app_state=AppState()

events=[]

#ルートのレスポンスをheatmap.htmlに設定
@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
    #APIキーを取得
    google_maps_api_key=AppState.google_maps_api_key
    if not google_maps_api_key:
        return {"error":"API key not found."}
    
    #HTMLテンプレートをレンダリングしてAPIキーを渡す
    return templates.TemplateResponse(
        "heatmap.html",
        {"request": request, "google_maps_api_key":google_maps_api_key}
    )

@app.get("/wait")
async def wait_endpoint():
    await asyncio.sleep(2)
    return {"msg":"2秒待ったよ"}

#DBにeventを追加する
@app.post("/insert_event")
def insert_events(events:List[Event]):
    with EventDAO(app_state.db_config) as dao:
        dao.insert_events(events)
    return {"msg":"added data."}

#DBからタイムスタンプの期間を指定してデータを取得する
@app.get("/get_events",response_model=List[Event])
def get_events(
    start: Optional[datetime]=None, #OptionalはNoneもしくは指定した型のどちらかであることを明示
    end: Optional[datetime]=None
):
    with EventDAO(app_state.db_config) as dao:
        #DBから取得した全イベントをEvent形式に変換してlistとしてまとめる
        db_events=dao.get_events_by_period(start,end)
        events=get_list(db_events)
        print(events)
    return events

#DBから全レコードを削除
@app.get("/delete_events")
def delete_events():
    with EventDAO(app_state.db_config) as dao:
        dao.delete_events()
        print(events)
    return{"msg":"deleted records."}

#テスト用データの追加
@app.get("/add_test_data")
def add_test_data():
    with open("sample_events.json","r",encoding="utf-8") as f:
        data=json.load(f)
    #JSON→List[Event]に変換
    events=[Event.parse_obj(e) for e in data]
    insert_events(events)

#DB環境 本番⇔テスト の切り替え
@app.get("/switch_db_config")
def switch_db_mode():
    app_state.switch_db_config()
    return {"msg":"db_config swithced"}



