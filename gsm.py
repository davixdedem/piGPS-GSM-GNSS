import time
import serial
import logging
import sqlite3
import RPi.GPIO as GPIO

class GSM():
    def __init__(self,port) -> None:
    
        self.receiverNumber = "+393475487544"
        self.localSMSC = "+393358824940"
        #AT+CSCA="+393358824940"
        #AT+CENG? --> Query the neighbords cell towers
        self.apn = "ibox.tim.it"
        self.debug = True
        self.log = LOG()
        self.conn = sqlite3.connect('/home/pi/data/generalDB.db', check_same_thread=False)
        self.port = port
        self.isGpsStopped = False
        self.powerPin = 4
        self.timer_keep_send_message = 600

        self.createTableMessage()
        self.createTableGps()   

    def edit_configuration(self, config_name, new_config_value):
        try:
            conn = sqlite3.connect('/home/pi/data/generalDB.db', check_same_thread=False)
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE configurations
                    SET config_value = ?
                    WHERE config_name = ?
                ''', (new_config_value, config_name))
                if cursor.rowcount > 0:
                    return True  
                else:
                    return False  
        except Exception as e:
            self.log.log_message(f"Caught exception on edit_configuration: {e}")
            return False 
        finally:
            if conn:
                conn.close() 

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

    def power_on_or_off(self, duration=4):
        try:
            GPIO.setmode(GPIO.BCM)
            try:
                GPIO.setup(self.powerPin, GPIO.OUT)
                GPIO.output(self.powerPin, GPIO.LOW)
                self.log.log_message(f"Pin {self.powerPin} set to 1 for {duration} seconds")
                time.sleep(duration)
            except Exception as e:
                self.log.log_message(f"Error setting power's pin: {e}")
        except Exception as e:
            self.log.log_message(f"Caught exc. on powerOn: {e}")
            return False
    
    def callNumber(self):
        try:
            self.writeCommand(f'AT\r\n'.encode("utf-8"))
            rcv = self.port.readline()  # Read until a new line is encountered
            self.log.log_message(f"Answer to AT: {rcv.decode('utf-8').strip()}")  # Decode and strip newline characters
            time.sleep(1)   

            self.writeCommand(f'AT+CGNSPWR=0\r\n'.encode("utf-8"))
            rcv = self.port.readline() 
            self.log.log_message(f"Answer to AT+CGNSPWR=0: {rcv.decode('utf-8').strip()}") 
            time.sleep(1)              

            self.writeCommand(f'ATD{self.receiverNumber};\r\n'.encode("utf-8"))
            rcv = self.port.readline()  # Read until a new line is encountered
            self.log.log_message(f"Answer to ATD: {rcv.decode('utf-8').strip()}")  # Decode and strip newline characters
            time.sleep(60)

            self.writeCommand(f'AT+CGNSPWR=1\r\n'.encode("utf-8"))
            rcv = self.port.readline() 
            self.log.log_message(f"Answer to AT+CGNSPWR=1: {rcv.decode('utf-8').strip()}") 
            time.sleep(1)              

        except Exception as e:
            self.log.log_message(f"Caught exc. on callNumber: {e}")
            return False
    
    def getLastCoordinates(self):
        try:
            conn = sqlite3.connect('/home/pi/data/generalDB.db', check_same_thread=False)
            cursor = conn.cursor()
            try:
                # Modify the query to exclude rows where latitude or longitude is 0 or NULL
                cursor.execute("SELECT latitude, longitude, timestamp FROM gps "
                            "WHERE latitude IS NOT NULL AND longitude IS NOT NULL "
                            "AND latitude != 0 AND longitude != 0 "
                            "ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    last_latitude, last_longitude, timestamp = row
                    return last_latitude, last_longitude, timestamp
                else:
                    return None, None, None
            except sqlite3.Error as e:
                print(f"SQLite error: {e}")
                return None, None, None
            finally:
                conn.close()
        except Exception as e:
            self.log.log_message(f"Caught exc. on getLastCoordinates: {e}")
            return False
    
    def send_a_message_every_n_minutes(self):
        try:
            while True:
                time.sleep(self.timer_keep_send_message)
                self.sendMessage()
        except Exception as e:
            self.log.log_message(f"Caught exc. on send_a_message_every_n_minutes: {e}")
            return False
    
    def setupSIM(self):
        try:
            self.writeCommand(f'AT+CSTT={self.apn}\r\n'.encode("utf-8"))
            rcv = self.port.readline() 
            self.log.log_message(f"Answer to AT+CSTT={self.apn}: {rcv.decode('utf-8').strip()}")  # Decode and strip newline characters
            time.sleep(1)            

            self.writeCommand(f'AT+CNMI=2,2,0,0,0\r\n'.encode("utf-8"))
            rcv = self.port.readline() 
            self.log.log_message(f"Answer to AT+CNMI=2,2,0,0,0: {rcv.decode('utf-8').strip()}")  # Decode and strip newline characters
            time.sleep(1)         

            self.writeCommand(f'AT+CMGF=1\r\n'.encode("utf-8"))
            rcv = self.port.readlines()
            self.log.log_message(f"Answer to AT+CMGF=1: {rcv[1].decode('utf-8').strip()}")                
        except Exception as e:
            self.log.log_message(f"Caught exc. on setupSIM: {e}")
            return False
    
    def readAllUnreadMessages(self):
        try:
            self.writeCommand(f'AT+CSTT={self.apn}\r\n'.encode("utf-8"))
            rcv = self.port.readline() 
            self.log.log_message(f"Answer to AT+CSTT={self.apn}: {rcv.decode('utf-8').strip()}")  # Decode and strip newline characters
            time.sleep(1)                        
        except Exception as e:
            self.log.log_message(f"Caught exc. on setupSIM: {e}")
            return False        

    def startAndStopGPS(self,stop=False):
        try:
            if not stop:
                self.writeCommand(f'AT+CGNSPWR=1\r\n'.encode("utf-8"))
                rcv = self.port.readline() 
                self.log.log_message(f"Answer to AT+CGNSPWR=1: {rcv.decode('utf-8').strip()}")  # Decode and strip newline characters
                time.sleep(1)    
            else:
                self.writeCommand(f'AT+CGNSPWR=0\r\n'.encode("utf-8"))
                rcv = self.port.readline() 
                self.log.log_message(f"Answer to AT+CGNSPWR=0: {rcv.decode('utf-8').strip()}")  
                time.sleep(1)    
        except Exception as e:
            self.log.log_message(f"Caught exc. on startAndStopGPS: {e}")
            return False  
    
    def readMessageByNumber(self,number,gpsHasMoved=False,distance=False):
        try:
            try:
                self.log.log_message(f"I got the number {number}")
                if number == "007":
                    self.log.log_message(f"Received a valid code: {number}, I'm going to answer back with gps data.")
                    coordinates = self.getLastCoordinates()
                    if coordinates:
                        self.writeCommand(f'AT+CGNSPWR=0\r\n'.encode("utf-8"))
                        rcv = self.port.readline() 
                        self.log.log_message(f"Answer to AT+CGNSPWR=1: {rcv.decode('utf-8').strip()}") 
                        time.sleep(1)  

                        if not gpsHasMoved:
                            message=str(f"GPS:{coordinates[0]},{coordinates[1]} - DT: {coordinates[2]}.")
                        else:
                            message = f"Device has moved about {distance} meters. GPS:{coordinates[0]},{coordinates[1]} - DT: {coordinates[2]}."

                        self.sendMessage(message=message)
                        self.writeCommand(f'AT+CGNSPWR=1\r\n'.encode("utf-8"))
                        rcv = self.port.readline() 
                        self.log.log_message(f"Answer to AT+CGNSPWR=1: {rcv.decode('utf-8').strip()}") 
                        time.sleep(1)  
                        return True
                elif number == "008":
                    self.log.log_message("I'm going to activate on time alerting(OTA)..")
                    ota_mode = self.get_configuration("otaMode")
                    if ota_mode in ["0", "1"]:
                        new_ota_mode = "1" if ota_mode == "0" else "0"
                        self.edit_configuration("otaMode", new_ota_mode)
            except Exception as e:
                self.writeCommand(f'AT+CGNSPWR=1\r\n'.encode("utf-8"))
                rcv = self.port.readline() 
                self.log.log_message(f"Answer to AT+CGNSPWR=1: {rcv.decode('utf-8').strip()}") 
                time.sleep(1) 
                self.log.log_message(f"Caught1 exc. on readMessageByNumber: {e}")
        except Exception as e:
            self.writeCommand(f'AT+CGNSPWR=1\r\n'.encode("utf-8"))
            rcv = self.port.readline() 
            self.log.log_message(f"Answer to AT+CGNSPWR=1: {rcv.decode('utf-8').strip()}") 
            time.sleep(1) 
            self.log.log_message(f"Caught2 exc. on readMessageByNumber: {e}")
            return False

    def sendMessage(self, message):
        try:
            self.writeCommand(f'AT\r\n'.encode("utf-8"))
            rcv = self.port.readlines()
            self.log.log_message(f"Answer to AT: {rcv[1].decode('utf-8').strip()}")

            self.writeCommand(f'AT+CSCA=\"{self.localSMSC}\"\r\n'.encode("utf-8"))
            rcv = self.port.readlines()
            self.log.log_message(f"Answer to AT+CSCA='{self.localSMSC}': {rcv[1].decode('utf-8').strip()}")

            self.writeCommand(f'AT+CMGF=1\r\n'.encode("utf-8"))
            rcv = self.port.readlines()
            self.log.log_message(f"Answer to AT+CMGF=1: {rcv[1].decode('utf-8').strip()}")

            self.writeCommand(f'AT+CMGS=\"{self.receiverNumber}\"\r\n'.encode("utf-8"))
            rcv = self.port.readlines()

            self.writeCommand(f'{message}\r\n'.encode("utf-8"))
            rcv = self.port.readlines()

            self.writeCommand("\x1A".encode("utf-8"))
            for i in range(10):
                rcv = self.port.readlines()
                try:
                    if rcv[1].decode('utf-8').strip() == "ERROR":
                        self.log.log_message(f"Could not sent '{message}' to {self.receiverNumber}")
                    if rcv[1].decode('utf-8').strip() == "OK":
                        self.log.log_message(f"Succesfully sent '{message}' to {self.receiverNumber}")
                except:
                    pass
            self.insertMessage(message, "1")
        except Exception as e:
            self.log.log_message(f"Caught exc. on sendMessage: {e}")
            return False
        
    def check_if_device_is_turned_on(self):
        try:
            self.log.log_message("I'm going to check if device is on...")
            self.port.write(b'AT\r\n')
            response = self.port.read(100).decode('utf-8').strip()
            if "OK" in response:
                self.log.log_message("Device is already turned on and responded to AT command.")
                return True
            else:
                self.log.log_message("Device is not responding as expected, maybe it's still off.")
                return False
        except serial.SerialException as e:
            self.log.log_message(f"Caught exception on check_if_device_is_turned_on: {e}")
            return False
        
    def sendMessageThroughTelegram(self, message):
        try:
            token = "6921961644:AAF_KpsAgomp5QBVVjWC_El6Lytk1BAGEOA"
            chat_id = "838137784"
            url_req = "api.telegram.org:443/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + message 

            self.writeCommand(f'AT+HTTPTERM\r\n'.encode("utf-8"))
            rcv = self.port.readlines()
            self.log.log_message(f"Answer to AT+HTTPTERM: {rcv[1].decode('utf-8').strip()}")   

            self.writeCommand(f'AT+HTTPINIT\r\n'.encode("utf-8"))
            rcv = self.port.readlines()
            self.log.log_message(f"Answer to AT+HTTPINIT: {rcv[1].decode('utf-8').strip()}")

            self.writeCommand(f'AT+HTTPPARA="REDIR",1\r\n'.encode("utf-8"))
            rcv = self.port.readlines()
            self.log.log_message(f"Answer to AT+HTTPPARA='REDIR',1: {rcv[1].decode('utf-8').strip()}")

            self.writeCommand(f'AT+HTTPPARA="CID","1"\r\n'.encode("utf-8"))
            rcv = self.port.readlines()
            self.log.log_message(f"Answer to AT+HTTPPARA='CID',1: {rcv[1].decode('utf-8').strip()}")

            self.writeCommand(f'AT+HTTPPARA="URL",{url_req}\r\n'.encode("utf-8"))
            rcv = self.port.readlines()
            self.log.log_message(f"Answer to AT+HTTPPARA='URL','{url_req}',1: {rcv[1].decode('utf-8').strip()}")     

            self.writeCommand(f'AT+HTTPSSL=1\r\n'.encode("utf-8"))
            rcv = self.port.readlines()
            self.log.log_message(f"Answer to AT+HTTPSSL=1: {rcv[1].decode('utf-8').strip()}")    

            self.writeCommand(f'AT+HTTPACTION=0\r\n'.encode("utf-8"))
            rcv = self.port.readlines()
            self.log.log_message(f"Answer to AT+HTTPACTION=0: {rcv[1].decode('utf-8').strip()}")     

            self.writeCommand(f'AT+HTTPREAD\r\n'.encode("utf-8"))
            rcv = self.port.readlines()
            self.log.log_message(f"Answer to AT+HTTPREAD: {rcv[1].decode('utf-8').strip()}")    

            self.writeCommand(f'AT+HTTPTERM\r\n'.encode("utf-8"))
            rcv = self.port.readlines()
            self.log.log_message(f"Answer to AT+HTTPTERM: {rcv[1].decode('utf-8').strip()}")                                                  
        except Exception as e:
            self.log.log_message(f"Caught exc. on sendMessageThroughTelegram: {e}")
            return False        

    def createTableGps(self):
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS gsm (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    receiverNumber REAL NULL,
                    senderNumber REAL NULL,
                    communicationType REAL NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except Exception as e:
            self.log.log_message(f"Caught exc. on createTable: {e}")
            return False
        
    def createTableMessage(self):
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    context TEXT NULL,
                    sent INT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except Exception as e:
            self.log.log_message(f"Caught exc. on createTable: {e}")
            return False            
        
    def insertMessage(self,message,sent):
        try:
            self.cursor.execute('''
                INSERT INTO messages (context, sent) VALUES (?, ?)
                                ''', (message, sent))
            self.conn.commit()
        except Exception as e:
            self.log.log_message(f"Caught exc. on insertMessage: {e}")
            return False
        
    def writeCommand(self,command):
        try:
            self.port.write(command)
        except Exception as e:
            self.log.log_message(f"Caught exc. on writeCommand:{e}")    
            return False

    def initGSM(self):
        try:
            pass
        except Exception as e:
            self.log.log_message(f"Caught exc. on initGSM:{e}")    
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