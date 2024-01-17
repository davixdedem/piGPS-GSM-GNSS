#!/usr/bin/python
import gps
import gsm
import gpio
import time
import serial
import database
from threading import Thread

if __name__ == "__main__":
    port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=5)
    timer_sleep = 4

    #--GSM--#
    gsm = gsm.GSM(port)

    #--GPS--#
    gps = gps.GPS(port,gsm)
    tGPSReadingData = Thread(target=gps.readingData)
    tSyncingTime = Thread(target=gps.startSyncingTime)

    #--GPIO--#
    #gpio = gpio.GPIO()
    #tGpioReading = Thread(target=gpio.startReading)

    #--DATABASE--#
    db = database.DATABASE()
    tFlushTables = Thread(target=db.startFlushingOnTime)

    # -- Turning on the device if it is not already turned on, otherwise restart it -- #
    deviceIsOn = False
    deviceWasOff = False

    deviceIsOn = gsm.check_if_device_is_turned_on()
    if deviceIsOn:
        print("Device is on...")
        while deviceIsOn:
            tPowerOnOffDevice = Thread(target=gsm.power_on_or_off)
            tPowerOnOffDevice.start()
            time.sleep(timer_sleep)
            deviceIsOn = gsm.check_if_device_is_turned_on()
            if deviceIsOn:
                tPowerOnOffDevice.join()
                time.sleep(timer_sleep)
            else:
                break
        while not deviceIsOn:
            tPowerOnOffDevice = Thread(target=gsm.power_on_or_off)
            tPowerOnOffDevice.start()
            time.sleep(timer_sleep)
            deviceIsOn = gsm.check_if_device_is_turned_on()
            if not deviceIsOn:
                tPowerOnOffDevice.join()
                time.sleep(timer_sleep)
            else:
                break

    elif not deviceIsOn:
        while not deviceIsOn:
            tPowerOnOffDevice = Thread(target=gsm.power_on_or_off)
            tPowerOnOffDevice.start()
            deviceIsOn = gsm.check_if_device_is_turned_on()
            if not deviceIsOn:
                tPowerOnOffDevice.join()
                time.sleep(timer_sleep)

    gps.stopDevice()
    time.sleep(timer_sleep)

    gsm.setupSIM()
    time.sleep(timer_sleep)
    
    gps.initDevice()
    time.sleep(timer_sleep)

    #tGpioReading.start()
    tSyncingTime.start()
    tFlushTables.start()
    tGPSReadingData.start()