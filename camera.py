import json
import logging
import picamera
from datetime import datetime
from gpiozero import Button

CONFIGURATION_PATH = "/home/pi/piHat/configuration"

class CAMERA():
    def __init__(self) -> None:
        self.camera = picamera.PiCamera()
        self.setupDevice()
        self.log_file = self.read_configuration(CONFIGURATION_PATH,"logPath")
        self.videoPath = self.read_configuration(CONFIGURATION_PATH,"videoPath")
        self.video_filename = None
        self.debug = True
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ])

    def read_configuration(self, file_path, key):
        try:
            with open(file_path, 'r') as file:
                configuration_data = json.load(file)
                return configuration_data.get(key, None)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Error: File '{file_path}' not found.") from e
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error decoding JSON in file '{file_path}': {e}", doc=e.doc, pos=e.pos) from e
        except Exception as e:
            raise Exception(f"An error occurred: {e}") from e

    def setupDevice(self):
        try:
            self.camera.resolution = (640, 480)
            self.camera.framerate = 30
        except Exception as e:
            self.log_message(f"Caught exc. on setupDevice: {e}")
            return False
        
    def recordVideo(self):
        try:
            current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            video_filename = f"video_{current_datetime}.h264"
            self.video_filename = video_filename
            self.log_message("Start recording...")
            self.camera.start_recording(self.videoPath + video_filename, format='h264')
        except Exception as e:
            self.log_message(f"An error occurred: {e}")
        finally:
            self.camera.stop_recording()
            self.camera.close()
            self.log_message(f"Video recorded as {self.video_filename}")

    def log_message(self, message):
        if self.debug:
            logging.info(message)