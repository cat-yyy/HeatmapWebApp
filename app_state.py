import os
from dotenv import load_dotenv
import threading

#.envを読み込み
load_dotenv()

#開発DB用のコンフィグ定数
MAMP_DB_CONFIG={
    "host":os.getenv("MAMP_HOST"),
    "port":int(os.getenv("MAMP_PORT")),
    "user":os.getenv("MAMP_USER"),
    "password":os.getenv("MAMP_PASSWORD"),
    "database":os.getenv("MAMP_DATABASE")
}

#本番DB用のコンフィグ定数
RAILWAY_DB_CONFIG={
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
        self._db_config=MAMP_DB_CONFIG
        #スレッドロックのためのカギを作成
        self.lock = threading.Lock()

    @property
    def db_config(self):
        return self._db_config
    
    @db_config.setter
    def db_config(self,value):
        self._db_config=value

    #コンフィグの値を開発用⇔本番用でスイッチする
    def switch_db_config(self):
        #withブロック内で排他制御をする
        with self.lock:
            if self.db_config!=MAMP_DB_CONFIG:
                self.db_config=MAMP_DB_CONFIG #setter呼び出し
            else:
                self.db_config=RAILWAY_DB_CONFIG #setter呼び出し

