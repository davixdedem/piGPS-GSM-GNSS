import time
import sqlite3
import logging
from datetime import datetime, timedelta

class DATABASE():
    def __init__(self) -> None:
        self.log = LOG()
        self.debug = True
        self.dbPath = "/home/pi/data/generalDB.db"
        self.flushTimer = 300
        self.tables_to_flush = {
            "table1": "gps",
            "table2": "motionDetection",
        } 

    def flushTable(self):
        try:
            conn = sqlite3.connect(self.dbPath)
            cursor = conn.cursor()
            five_days_ago = datetime.now() - timedelta(days=5)
            five_days_ago_str = five_days_ago.strftime("%Y-%m-%d")
            for table, date_column in self.tables.items():
                query = f"DELETE FROM {table} WHERE {date_column} < '{five_days_ago_str}'"
                cursor.execute(query)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.log_message(f"Caught exc. on flushTable: {e}")
            return False
        
    def log_message(self,message):
        if self.debug:
            logging.info(message)        
    
    def startFlushingOnTime(self):
        try:
            while True:
                time.sleep(self.flushTimer)
                self.flushTable()
        except Exception as e:
            self.log.log_message(f"Caught exc. on startFlushingOnTime: {e}")

class LOG():
    def __init__(self) -> None:
        self.log_file = '/home/pi/piHat/logs/database.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ])    

    def log_message(self,message):
        if self.debug:
            logging.info(message)  