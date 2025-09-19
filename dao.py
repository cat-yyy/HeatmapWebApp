from models import Event
from mysql.connector import Error
from typing import List
import mysql.connector
import yaml
from datetime import datetime

# config.yamlからDBのカラム名を読み込む
try:
    with open("config.yaml", "r", encoding="utf-8") as f:
        CONFIG = yaml.safe_load(f)
        DB_COLUMNS = CONFIG["database_columns"]
except FileNotFoundError as e:
    print(f"config.yamlが見つからない{e}")
    exit(1)


class EventDAO:
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None

    # with文のブロックが開始される直前に呼ばれる
    def __enter__(self):
        try:
            # connはDBとの接続を担う
            self.conn = mysql.connector.connect(
                **self.db_config
            )  # **で辞書をキーワード引数として展開できる
            return self
        except Error as e:
            print(f"データベース接続エラー{e}")
            raise

    # with文のブロックが終了した直後に呼ばれる
    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn and self.conn.is_connected():
            self.conn.close()

    # データ挿入
    def insert_events(self, events: List[Event]) -> None:
        sql = f"""
        INSERT INTO events (
            {DB_COLUMNS["id"]},
            {DB_COLUMNS["pushed_timestamp"]},
            {DB_COLUMNS["name"]},
            {DB_COLUMNS["location_lat"]},
            {DB_COLUMNS["location_lon"]}
        )
        VALUES (%s, %s, %s, %s, %s)
        """
        data = [
            (e.id, e.pushed_timestamp, e.name, e.location.lat, e.location.lon)
            for e in events
        ]
        cursor = None  # cursorはSQLクエリを実行する役割
        try:
            cursor = self.conn.cursor()
            # 複数のタプルにsqlを実行
            cursor.executemany(sql, data)
            self.conn.commit()
            print("insert_eventが正常に終了")
        except Error as e:
            print(f"データ挿入中にエラーが発生:{e}")
            self.conn.rollback()
            # エラーを呼び出し元へ伝播 fainally→raiseの順
        finally:
            if cursor:
                cursor.close()

    # データの取得 すべてのイベントを取得してlistで返す
    def get_all_events(self) -> list:
        sql = """SELECT * FROM events
        """
        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)  # 辞書形式で結果を取得
            cursor.execute(sql)
            results = cursor.fetchall()  # すべての結果を取得
            print("get_all_eventが正常に終了")
        except Error as e:
            print(f"get_all_eventにエラー発生:{e}")
            raise
        finally:
            if cursor:
                cursor.close()
        return results

    # テーブルから全レコードを削除する
    def delete_events(self) -> None:
        sql = """DELETE FROM events
            """
        cursor = None
        try:
            corsor = self.conn.cursor()
            corsor.execute(sql)
            self.conn.commit()
            print("全レコードの削除が完了")
        except Error as e:
            print(f"DELETE中にエラーが発生:{e}")
            self.conn.rollback()
        finally:
            if cursor:
                cursor.close()

    # 期間絞り込み
    def get_events_by_period(self, start: datetime = None, end: datetime = None):
        sql = "SELECT * FROM events"
        params = []

        # WHERE句を動的に作る
        where_clauses = []
        if start:
            where_clauses.append(f"{DB_COLUMNS['pushed_timestamp']} >= %s")
            params.append(start)
        if end:
            where_clauses.append(f"{DB_COLUMNS['pushed_timestamp']} <= %s")
            params.append(end)
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        cursor = None
        try:
            cursor = self.conn.cursor(dictionary=True)  # 辞書形式で結果を取得
            cursor.execute(sql, tuple(params))
            results = cursor.fetchall()
        except Error as e:
            print(f"get_event_by_period中にエラーが発生:{e}")
            raise
        finally:
            cursor.close()

        return results
