from google import genai
import os
from dotenv import load_dotenv
from models import Event
import json


# .env読み込み
load_dotenv()
# Geminiの使用モデル
GEMINI_MODLE = "gemini-2.5-flash"
# APIキー
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")


# Geminiに送信するトークンの数を節約するためにデータを加工して、
# str型のクエリとして返す
def procces_data(events) -> str:
    # #Eventのlist
    # events=[]
    # Eventのnameを格納するdict型
    names = {}
    # timestampのリスト(集計期間がいつからいつまでかを取得するために必要)
    timestamps = []
    # 各時刻(0~23時)における各nameの数をここに格納する
    timestamp_dict = {
        0: {},
        1: {},
        2: {},
        3: {},
        4: {},
        5: {},
        6: {},
        7: {},
        8: {},
        9: {},
        10: {},
        11: {},
        12: {},
        13: {},
        14: {},
        15: {},
        16: {},
        17: {},
        18: {},
        19: {},
        20: {},
        21: {},
        22: {},
        23: {},
    }

    # #jsonデータはList[Event]型にまとめる
    # events=[Event(**e) for e in data] #Eventにキーワード引数として渡す

    # 各eventのnameだけを重複なく抽出
    for e in events:
        hour = e.pushed_timestamp.hour  # イベントの"時"を取得
        if not timestamp_dict.get(hour).get(e.name):  # 値がなければ１カウント
            timestamp_dict[hour][e.name] = 1
        else:
            timestamp_dict[hour][e.name] += 1
        timestamps.append(e.pushed_timestamp)
    query = f"""
    次のdict型のlistデータについて200文字程度で分析して。
    keyは時間帯を表す。valueの中の辞書は'要素:その時間帯における数'を表す。
    また集計期間は{min(timestamps)}から{max(timestamps)}までである。{timestamp_dict}
    """
    return query


# json型のデータをgeminiに渡して、そのレスポンスをそのまま返す
def request_gemini(events):
    if not events:
        print("データがありません")
        return
    # データを加工し、そのクエリを取得
    query = procces_data(events)
    print(f"命令{query}")

    client = genai.Client(api_key=GOOGLE_GEMINI_API_KEY)

    response = client.models.generate_content(model=GEMINI_MODLE, contents=query)
    return response


# #jsonデータを読ませる
# with open("events.json","r",encoding="utf-8") as f:
#     data=json.load(f)
#     print(request_gemini(data).text)
