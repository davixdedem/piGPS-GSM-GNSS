import picamera
import logging
from datetime import datetime
from gpiozero import Button

class CAMERA():
    def __init__(self) -> None:
        self.camera = picamera.PiCamera()
        self.setupDevice()
        self.log_file = '/home/pi/piHat/logs/gps.log'
        self.videoPath = "/home/pi/Videos/"
        self.video_filename = None
        self.debug = True
        self.button = Button(17)  # Change to the appropriate GPIO pin
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
            self.button.wait_for_press()  # Wait for the button press to stop recording
        except Exception as e:
            self.log_message(f"An error occurred: {e}")
        finally:
            self.camera.stop_recording()
            self.camera.close()
            self.log_message(f"Video recorded as {self.video_filename}")

    def log_message(self, message):
        if self.debug:
            logging.info(message)