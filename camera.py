import picamera
import logging
from datetime import datetime

class CAMERA():
    def __init__(self) -> None:
        self.camera = picamera.PiCamera()
        self.setupDevice()
        self.log_file = '/home/pi/piHat/logs/camera.log'
        self.videoPath = "/home/pi/Videos/"
        self.video_filename = None
        self.debug = True
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ])               

    def setupDevice(self):
        try:
            self.camera.resolution = (640, 480)
            self.camera.framerate = 30
            self.video_duration = 10
        except Exception as e:
            self.log_message(f"Caught exc. on setupDevice: {e}")
            return False
        
    def recordVideo(self):
        try:
            current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            video_filename = f"video_{current_datetime}.h264"
            self.video_filename = video_filename
            self.log_message("Start to recording...")
            self.camera.start_recording(self.videoPath+video_filename)
            self.camera.wait_recording(self.video_duration)
        except Exception as e:
            self.log_message(f"An error occurred: {e}")
        finally:
            self.camera.close()
    
    def stopRecording(self):
        try:
            self.camera.stop_recording()
            self.log_message(f"Video recorded as {self.video_filename}")
        except Exception as e:
            self.log_message(f"Caught exc. on stopRecording:{e}")

    def log_message(self,message):
        if self.debug:
            logging.info(message)    