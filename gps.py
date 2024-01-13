import os
import time
import signal
import logging
import sqlite3
import pynmea2
from datetime import datetime

class SYNC():
    def __init__(self) -> None:
        self.log = LOG()

    def syncTime(self, timestamp_str):
        try:
            date, time = str(timestamp_str).split(' ')
            set_date_command = f"sudo date -s {date}"
            os.system(set_date_command)
            set_time_command = f"sudo date -s {time}"
            os.system(set_time_command)
            return True
        except Exception as e:
            self.log.log_message(f"Caught exc. on syncTime: {e}")
            return False

class GPS():
    def __init__(self,port,gsm) -> None:
        self.debug = True
        self.timer = 120
        self.timer_sync_ntp = 150
        self.log_file = '/home/pi/piHat/gps.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ])
        self.latitude = None
        self.longitude = None
        self.altitude = None
        self.groundSpeed = None
        self.latDir = None
        self.longDir = None
        self.satellites = None
        self.geoidSeparation = None
        self.pDop = None
        self.hDop = None
        self.vDop = None
        self.satInformation = None
        self.fixQuality = None
        self.totalMessages = None
        self.messageNumber = None
        self.satelitesInView = None
        self.timestampGPS = None
        self.createTable()
        self.log = LOG()
        self.sync = SYNC()
        self.port = port
        self.gsm = gsm
        self.log.log_message("Successfully opened port...")
        signal.signal(signal.SIGINT, self.close_connection)

    def createTable(self):
        try:
            self.conn = sqlite3.connect('/home/pi/data/generalDB.db', check_same_thread=False)
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS gps (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        latitude REAL NULL,
                        longitude REAL NULL,
                        altitude REAL NULL,
                        groundSpeed REAL NULL,
                        latDir REAL NULL,
                        longDir REAL NULL,
                        satellites REAL NULL,
                        geoidSeparation REAL NULL,
                        pDop REAL NULL,
                        hDop REAL NULL,
                        vDop REAL NULL,
                        satInformation TEXT NULL,
                        fixQuality REAL NULL,
                        totalMessages REAL NULL,
                        messageNumber REAL NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
        except Exception as e:
            self.log.log_message(f"Caught exc. on createTable: {e}")
            return False
    
    def get_configuration(self, config_name):
        try:
            conn = sqlite3.connect('/home/pi/data/generalDB.db', check_same_thread=False)
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT config_value
                    FROM configurations
                    WHERE config_name = ?
                ''', (config_name,))
                result = cursor.fetchone()
                if result:
                    return result[0] 
                else:
                    return None  
        except Exception as e:
            self.log.log_message(f"Caught exception on get_configuration: {e}")
            return None  
        finally:
            if conn:
                self.conn.close() 
        
    def find(self,str, ch):
        for i, ltr in enumerate(str):
            if ltr == ch:
                yield i
    
    def log_message(self,message):
        if self.debug:
            logging.info(message)

    def close_connection(self,signal, frame):
        self.log.log_message("Closing connection and exiting gracefully...")
        self.port.write('AT+CGNSTP\r\n'.encode("utf-8"))  # Stop GPS service
        self.port.close()  # Close the serial port
        self.cursor.close()  # Close the database cursor
        self.conn.close()  # Close the database connection
        exit(0)

    def writeCommand(self,command):
        try:
            self.port.write(command)
        except Exception as e:
            self.log.log_message(f"Caught exc. on writeCommand:{e}")
    
    def initDevice(self):
        try:
            self.writeCommand('AT\r\n'.encode("utf-8"))
            rcv = self.port.readline()  # Read until a new line is encountered
            self.log.log_message(f"Answer to AT: {rcv.decode('utf-8').strip()}")  # Decode and strip newline characters
            time.sleep(0.1)

            self.writeCommand('AT+CGNSPWR=1\r\n'.encode("utf-8"))    	 	# to power the GPS
            rcv = self.port.readline()  # Read until a new line is encountered
            self.log.log_message(f"Answer to AT+CGNSPWR=1: {rcv.decode('utf-8').strip()}")  # Decode and strip newline characters
            time.sleep(.1)

            self.writeCommand('AT+CGNSIPR=115200\r\n'.encode("utf-8")) # Set the baud rate of GPS
            rcv = self.port.readline()  # Read until a new line is encountered
            self.log.log_message(f"Answer to AT+CGNSIPR=115200: {rcv.decode('utf-8').strip()}")  # Decode and strip newline characters
            time.sleep(.1)

            self.writeCommand('AT+CGNSTST=1\r\n'.encode("utf-8"))    # Send data received to UART
            rcv = self.port.readline()  # Read until a new line is encountered
            self.log.log_message(f"Answer to AT+CGNSTST=1: {rcv.decode('utf-8').strip()}")  # Decode and strip newline characters
            time.sleep(.1)

            self.writeCommand('AT+CGNSINF\r\n'.encode("utf-8"))   	# log_message the GPS information
            rcv = self.port.readline()
            self.log.log_message(f"Answer to AT+CGNSINF: {rcv.decode('utf-8').strip()}")  # Decode and strip newline characters
            time.sleep(.1)
        except Exception as e:
            self.log.log_message(f"Caught exc. on initDevice: {e}")
            return False
    
    def stopDevice(self):
        try:
            self.writeCommand('AT\r\n'.encode("utf-8"))
            rcv = self.port.readline()  # Read until a new line is encountered
            self.log.log_message(f"Answer to AT: {rcv.decode('utf-8').strip()}")  # Decode and strip newline characters
            time.sleep(0.1)

            self.writeCommand('AT+CGNSPWR=0\r\n'.encode("utf-8"))  # to power off the GPS
            rcv = self.port.readline()  # Read until a new line is encountered
            self.log.log_message(f"Answer to AT+CGNSPWR=0: {rcv.decode('utf-8').strip()}")  # Decode and strip newline characters
            time.sleep(.1)
        except Exception as e:
            self.log.log_message(f"Caught exc. on stopDevice: {e}")
            return False
        
    def populeDb(self):
        try:
            self.conn = sqlite3.connect('/home/pi/data/generalDB.db', check_same_thread=False)
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO gps (latitude, longitude, altitude, groundSpeed, latDir, longDir, satellites,
                                geoidSeparation, pDop, hDop, vDop, satInformation, fixQuality,
                                totalMessages, messageNumber)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.latitude, self.longitude, self.altitude, self.groundSpeed, self.latDir, self.longDir, self.satellites, self.geoidSeparation,
                self.pDop, self.hDop, self.vDop, str(self.satInformation), self.fixQuality, self.totalMessages, self.messageNumber))
            self.conn.commit()
        except Exception as e:
            self.log.log_message(f"Caught exc. on populeDb: {e}")
            return False
        
    def readingData(self):
        try:
            start_time = time.time()
            ck = 1
            while ck == 1:
                try:
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    fd = self.port.readline()  
                    if fd:
                        decoded_data = fd.decode("utf-8").strip()  # Decode and strip newline characters
                        self.log.log_message(f"Reading port: {decoded_data}")
                        if b'$GNRMC' in fd:
                            self.log.log_message(f"Reading GNRMC string: {decoded_data}")
                            data_parts = decoded_data.split(',')  # Split data by comma
                            if len(data_parts) >= 13:
                                self.time_data = data_parts[1]  # Time
                                self.groundSpeed = data_parts[7]      # Speed
                            else:
                                self.log.log_message(f"Not enough informations from GNRMC data...")
                        elif b'$GLGSV' in fd:
                            data_parts = decoded_data.split(',')  # Split data by comma
                            if len(data_parts) >= 8:
                                self.totalMessages = int(data_parts[1]) 
                                message_number = int(data_parts[2])  
                                satellites_in_view = int(data_parts[3]) 
                                satellites_info = []
                                satellite_data = data_parts[4:]
                                for i in range(0, len(satellite_data), 4):
                                    if i + 3 < len(satellite_data):
                                        prn = satellite_data[i]  
                                        elevation = satellite_data[i + 1] 
                                        azimuth = satellite_data[i + 2] 
                                        snr = satellite_data[i + 3] 
                                        satellites_info.append({
                                            'PRN': prn,
                                            'Elevation': elevation,
                                            'Azimuth': azimuth,
                                            'SNR': snr
                                        })
                                self.messageNumber = message_number
                                self.satelitesInView = satellites_in_view
                                self.satInformation =  satellites_info
                        elif b'$GLGSA' in fd:
                            data_parts = decoded_data.split(',')  # Split data by comma
                            if len(data_parts) >= 17:
                                self.mode1 = data_parts[2]  
                                self.mode2 = data_parts[3]  
                                self.satellites_used = [data_parts[i] for i in range(4, 15) if data_parts[i]]
                                self.pDop = data_parts[15]  
                                self.hDop = data_parts[16]  
                                self.vDop = data_parts[17] 
                        elif b'$GNGGA' in fd:
                            try:
                                self.log.log_message(f"Reading GNGGA: {decoded_data}")
                                msg = pynmea2.parse(decoded_data)
                                self.latitude = msg.latitude
                                self.longitude = msg.longitude
                                if self.latitude is not None and self.longitude is not None:
                                    self.log.log_message(f"Latitude is {self.latitude} and longitude is {self.longitude}")
                                self.timestamp = msg.timestamp
                                if self.timestamp:
                                    timestamp_str = str(self.timestamp).split('+')[0]  # Extracting the timestamp without timezone offset
                                    time_data = timestamp_str.split(':')
                                    seconds_with_fraction = time_data[2].split('.')
                                    seconds = seconds_with_fraction[0]
                                    fractional_seconds = seconds_with_fraction[1] if len(seconds_with_fraction) > 1 else '0'
                                    today_date = datetime.now().date()
                                    combined_time = datetime.strptime(f"{time_data[0]}:{time_data[1]}:{seconds}.{fractional_seconds}", "%H:%M:%S.%f").time()
                                    combined_datetime = datetime.combine(today_date, combined_time)
                                    self.log.log_message(f"Datetime is: {combined_datetime}")
                                    self.timestampGPS = combined_datetime
                                self.fixQuality = msg.gps_qual
                                self.satellites = msg.num_sats
                                self.altitude = msg.altitude
                                self.geoidSeparation = msg.geo_sep
                                self.latDir = msg.lat_dir
                                self.longDir = msg.lon_dir
                            except Exception as e:
                                self.log.log_message(f"Could not extract values from msg: {e}")
                        elif b'$GNVTG' in fd:
                            data_parts = decoded_data.split(',')  # Split data by comma
                            if len(data_parts) >= 9:
                                self.true_track = data_parts[1]  # True track made good
                                self.magnetic_track = data_parts[3]  # Magnetic track made good
                                self.ground_speed_knots = data_parts[5]  # Ground speed in knots
                                self.ground_speed_kmh = data_parts[7]  # Ground speed in km/h
                        elif b'+CMT' in fd:
                            number = self.port.readline().decode('utf-8').strip()
                            self.log.log_message(f"I received a message: {fd}")
                            isMessageSent = self.gsm.readMessageByNumber(number)                            
                            if isMessageSent:
                                self.log.log_message("The message was succesfully sendt.")                                
                        if elapsed_time >= self.timer:
                            self.log.log_message(f"Writing gps data into db: lat:{self.latitude}, long:{self.longitude}, alt:{self.altitude}")
                            if str(self.latitude) != "0.0" and str(self.longitude) != "0.0":
                                self.populeDb()
                                ota_mode = self.get_configuration("otaMode")
                                if ota_mode == "1":
                                    self.log.log_message("I'm going to send a message as OTA is activated")
                                    isMessageSent = self.gsm.readMessageByNumber("007")                            
                                    if isMessageSent:
                                        self.log.log_message("The message was succesfully sendt.")                                        
                                    time.sleep(10)
                            start_time = time.time()
                        time.sleep(.1)
                except Exception as e:
                    self.log.log_message(f"Caught1 exc. on readingData: {e}")
        except Exception as e:
            self.log.log_message(f"Caught2 exc. on readingData: {e}")
            return False
        
    def startSyncingTime(self):
        try:
            while True:
                if self.timestampGPS:
                    time.sleep(self.timer_sync_ntp)
                    self.log.log_message(f"I'm going to syncing time from gps data with: {self.timestampGPS}...")
                    self.sync.syncTime(self.timestampGPS)
        except Exception as e:
            self.log.log_message(f"Caught exc. on startSyncingTime: {e}")
            return False           
        
class LOG():
    def __init__(self) -> None:
        self.log_file = '/home/pi/piHat/logs/gps.log'
        self.debug = True
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