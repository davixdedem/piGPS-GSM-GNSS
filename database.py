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
            "gps": "timestamp",
            "motionDetection": "timestamp",
            "messages": "timestamp",
            "gsm": "timestamp"
        }

    def flushTable(self):
        try:
            conn = sqlite3.connect(self.dbPath)
            cursor = conn.cursor()

            # Check if tables exist before attempting to delete
            existing_tables = [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")]

            for table, date_column in self.tables_to_flush.items():
                if table in existing_tables:
                    five_days_ago = datetime.now() - timedelta(days=5)
                    five_days_ago_str = five_days_ago.strftime("%Y-%m-%d")
                    
                    # Using a parameterized query to avoid SQL injection
                    query = f"DELETE FROM {table} WHERE {date_column} < ?"
                    cursor.execute(query, (five_days_ago_str,))
                else:
                    self.log_message(f"Table {table} does not exist in the database.")

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.log_message(f"Caught exception on flushTable: {e}")
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
        self.log_file = '/home/pi/piHat/logs/gps.log'
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