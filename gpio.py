import time
import logging
import camera
from gpiozero import Button

class GPIO():
    def __init__(self) -> None:
        self.pin_number = 17  
        self.button = Button(self.pin_number)
        self.log_file = '/home/pi/piHat/logs/gps.log'
        self.isRecording = False
        self.debug = True
        self.camera = camera.CAMERA()
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ])         

    def start_recording(self):
        self.log_message("Button pressed! Starting recording...")
        self.isRecording = True
        self.camera.recordVideo()

    def stop_recording(self):
        self.log_message("Button released! Stopping recording...")
        self.isRecording = False
        self.camera.stopRecording()

    def startReading(self):
        try:
            self.log_message("Start to reading from GPIO...")
            while True:
                if self.button.is_pressed:
                    self.start_recording()
                else:
                    if self.isRecording:
                        self.stop_recording()
                time.sleep(2)
        except Exception as e:
            self.log_message(f"Caught exc. on startReading: {e}")
        finally:
            self.button.close()

        
    def log_message(self, message):
        if self.debug:
            logging.info(message)