import random
import json
from datetime import datetime, timedelta

# 大阪駅の中心座標
OSAKA_LAT = 34.702485
OSAKA_LON = 135.495951

# 生成するレコードの数
RECORDS = 100

# タイプ（仮に5種類）
NAMES = ["name1", "name2", "name3", "name4", "name5"]


def random_location():
    # 大阪駅周辺でランダム座標を返す
    lat_offset = random.uniform(-0.01, 0.01)  # 約±1000m
    lon_offset = random.uniform(-0.01, 0.01)  # 約±1000m
    return {
        "lat": round(OSAKA_LAT + lat_offset, 6),
        "lon": round(OSAKA_LON + lon_offset, 6),
    }


def random_timestamp():
    # ピークを考慮したランダムな時刻を返す#
    # ピーク時間帯の重み付け
    peak_hours = (
        [random.randint(7, 9) for _ in range(30)]  # 朝ピーク
        + [random.randint(17, 19) for _ in range(30)]  # 夕方ピーク
        + [random.randint(11, 15) for _ in range(25)]  # 昼
        + [random.randint(0, 5) for _ in range(15)]  # 深夜
    )
    hour = random.choice(peak_hours)
    minute = random.randint(0, 59)
    dt = datetime(2025, 9, 21, hour, minute)
    return dt.isoformat()


def generate_events(n=100):
    events = []
    for i in range(1, n + 1):
        event = {
            "id": f"event{i}",
            "pushed_timestamp": random_timestamp(),
            "name": random.choices(
                NAMES, weights=[40, 30, 15, 10, 5], k=1  # 種類の偏り（例: name1多め）
            )[0],
            "location": random_location(),
        }
        events.append(event)
    return events


if __name__ == "__main__":
    events = generate_events(RECORDS)
    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)
    print("✅ events.json を生成しました！")
