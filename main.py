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
    gpio = gpio.GPIO()
    tGpioReading = Thread(target=gpio.startReading)

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
            print("I'm going to turn it off..")
            tPowerOnOffDevice.start()
            time.sleep(timer_sleep)
            deviceIsOn = gsm.check_if_device_is_turned_on()
            if deviceIsOn:
                print("Device is still on, I'm going to retry to turn it off...")
                tPowerOnOffDevice.join()
                time.sleep(timer_sleep)
            else:
                print("Succesfully turned off device...")
                break
        while not deviceIsOn:
            tPowerOnOffDevice = Thread(target=gsm.power_on_or_off)
            print("I'm going to turn it on...")
            tPowerOnOffDevice.start()
            time.sleep(timer_sleep)
            deviceIsOn = gsm.check_if_device_is_turned_on()
            if not deviceIsOn:
                print("Device is still off, I'm going to turn it on...")
                tPowerOnOffDevice.join()
                time.sleep(timer_sleep)
            else:
                print("Succesfully turned on device, go ahead.")
                break

    elif not deviceIsOn:
        print("Device is off...")
        while not deviceIsOn:
            tPowerOnOffDevice = Thread(target=gsm.power_on_or_off)
            print("I'm going to turn it on..")
            tPowerOnOffDevice.start()
            deviceIsOn = gsm.check_if_device_is_turned_on()
            if not deviceIsOn:
                print("Device is still off, I'm going to turn it on...")
                tPowerOnOffDevice.join()
                time.sleep(timer_sleep)

    gps.stopDevice()
    time.sleep(timer_sleep)

    gsm.setupSIM()
    time.sleep(timer_sleep)
    
    gps.initDevice()
    time.sleep(timer_sleep)

    tGpioReading.start()
    tSyncingTime.start()
    tFlushTables.start()
    tGPSReadingData.start()