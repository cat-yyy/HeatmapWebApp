from fastapi import FastAPI, Request, HTTPException
from models import Event, Location
from typing import List, Optional
import asyncio
from dao import EventDAO
from dict_converter import get_list
import json
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from app_state import AppState
import requests
from ai_api import request_gemini

app = FastAPI()


# 静的ファイルの公開
app.mount("/static", StaticFiles(directory="static"), name="static")

# templatesフォルダにあるHTMLファイルを使用
templates = Jinja2Templates(directory="static")

app_state = AppState()

events = []


# ルートのレスポンスをheatmap.htmlに設定
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # APIキーを取得
    google_maps_api_key = AppState.google_maps_api_key
    if not google_maps_api_key:
        return {"error": "API key not found."}

    # HTMLテンプレートをレンダリングしてAPIキーを渡す
    return templates.TemplateResponse(
        "heatmap.html", {"request": request, "google_maps_api_key": google_maps_api_key}
    )


@app.get("/wait")
async def wait_endpoint():
    await asyncio.sleep(2)
    return {"msg": "2秒待ったよ"}


# DBにeventを追加する
@app.post("/insert_event")
def insert_events(events: List[Event]):
    with EventDAO(app_state.db_config) as dao:
        dao.insert_events(events)
    return {"msg": "added data."}


# DBからタイムスタンプの期間を指定してデータを取得する
@app.get("/get_events", response_model=List[Event])
def get_events(
    start: Optional[
        datetime
    ] = None,  # OptionalはNoneもしくは指定した型のどちらかであることを明示
    end: Optional[datetime] = None,
):
    with EventDAO(app_state.db_config) as dao:
        # DBから取得した全イベントをEvent形式に変換してlistとしてまとめる
        db_events = dao.get_events_by_period(start, end)
        events = get_list(db_events)
        print(f"number of records :{len(events)}")
    return events


# DBから全レコードを削除
@app.delete("/delete_events")
def delete_events():
    with EventDAO(app_state.db_config) as dao:
        dao.delete_events()
        print(events)
    return {"msg": "deleted records."}


# テスト用データの追加
@app.get("/add_test_data")
def add_test_data():
    with open("events.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    # JSON→List[Event]に変換
    events = [Event.parse_obj(e) for e in data]
    insert_events(events)


# DB環境 本番⇔テスト の切り替え
@app.get("/switch_db_env")
def switch_db_env(db_env: str):
    app_state.set_db_config(db_env)
    return {"msg": "db_config swithced"}


@app.get("/api/get_maps_data")
def get_maps_data(request: Request):
    # フロントエンドからのリクエストパラメータを取得
    query_params = request.query_params

    # Google Maps APIキーを取得
    google_maps_api_key = AppState.google_maps_api_key
    if not google_maps_api_key:
        return {"error: API KEY not found"}

    # APIへリクエストするURL
    url = f"https://maps.googleapis.com/maps/api/js?key={google_maps_api_key}&libraries=visualization"

    try:
        # APIへリクエスト
        response = requests.get(url)
        # HTTPエラーが発生したら例外をスロー
        response.raise_for_status()

        # 取得したjsのコードをフロント返す
        return HTMLResponse(content=response.text, status_code=response.status_code)

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch from Google Maps API:{e}"}


# GeminiAPIにリクエストする
@app.post("/api/ai")
async def ai(events: List[Event]):
    # 引数が空だった場合404を返す
    if not events:
        raise HTTPException(status_code=404, detail="error:events not found")
    text = request_gemini(events).text  # Geminiが答えるテキスト
    print(text)
    return text
