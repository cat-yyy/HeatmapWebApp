import os
from dotenv import load_dotenv
import threading

#.envを読み込み
load_dotenv()

#開発DB用のコンフィグ定数
TEST_DB_CONFIG={
    "host":os.getenv("TEST_HOST"),
    "port":int(os.getenv("TEST_PORT")),
    "user":os.getenv("TEST_USER"),
    "password":os.getenv("TEST_PASSWORD"),
    "database":os.getenv("TEST_DATABASE")
}

#本番DB用のコンフィグ定数
PRODUCTION_DB_CONFIG={
    "host":os.getenv("MYSQLHOST"),
    "port":int(os.getenv("MYSQLPORT")),
    "user":os.getenv("MYSQLUSER"),
    "password":os.getenv("MYSQLPASSWORD"),
    "database":os.getenv("MYSQLDATABASE")
}

class AppState:
    #GoogleMapのAPIキー
    google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY")

    def __init__(self):
        self._db_config=PRODUCTION_DB_CONFIG
        #スレッドロックのためのカギを作成
        self.lock = threading.Lock()

    @property
    def db_config(self):
        return self._db_config
    
    @db_config.setter
    def db_config(self,value):
        self._db_config=value

    #コンフィグの値を開発用⇔本番用でスイッチする
    def set_db_config(self,db_env):
        #withブロック内で排他制御をする
        with self.lock:
            if db_env=="test":
                self.db_config=TEST_DB_CONFIG #setter呼び出し
                print("DB mode is TEST")
            elif db_env=="production":
                self.db_config=PRODUCTION_DB_CONFIG #setter呼び出し
                print("DB mode is PRODUCTION")
            else:
                print("db_env is required")
                raise Exception 
