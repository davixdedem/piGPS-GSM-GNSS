**Raspberry Pi - GSM/GPRS/GNSS/CCTV**

This project integrates GSM (Global System for Mobile Communications) for mobile communication, GPRS (General Packet Radio Service) for efficient data transmission, and GNSS (Global Navigation Satellite System) for precise positioning. Additionally, it incorporates a CCTV (Closed-Circuit Television) system using video cameras for surveillance. Together, these technologies enable a comprehensive solution with mobile communication, data connectivity, accurate navigation, and visual monitoring capabilities."<br>

- ## **Description**
Thanks to the GSM/GPRS/GNSS board for Raspberry Pi, we will be able to monitor the current position of our SBC using GPS coordinates by GSM text messages. 
On the GPIO side, they will listen for all impulses and if one of those is detected, the PiCamera will start recording a video.<br>
![Screencast](screencast.png) <br>

In the context of this project, we use the following **GSM/GPRS/GNSS board**: (https://files.waveshare.com/upload/4/4a/GSM_GPRS_GNSS_HAT_User_Manual_EN.pdf)

- ## Step By Step
1. [Prerequisites](#prerequisites)<br>
2. [Device Preparation](#preparazione)<br>
3. [Setup](#configurazione)<br>
4. [Pros & Cons](#pros-and-cons)<br>
5. [Curiosities](#curiosities)<br>
6. [Support](#support)<br>
   
- # 1. Prerequisites <div id="prerequisites"></div>
**CubeCell – AB01 Dev-Board**: Heltec development board.<br>
**USB Cable**: USB cable to connect the board to the Smartphone.

## Where to GSM/GPRS/GNSS board for Raspberry Pi?
![HTTCAB01](hatgps.png)<br>
*CubeCell – AB01 Dev-Board*<br>
[Heltec](https://heltec.org/project/htcc-ab01-v2/)|[Amazon](https://www.amazon.it/LoRaWAN-sviluppo-ASR6501-energetico-Intelligent/dp/B07ZH7NL38/ref=sr_1_1?__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=2E73JV8F1KPLV&keywords=heltec+cubecell&qid=1701754977&sprefix=heltec+cubecel%2Caps%2C148&sr=8-1)|[Aliexpress](https://it.aliexpress.com/item/1005005444339915.html?spm=a2g0o.productlist.main.3.1d7150b2TFr0YZ&algo_pvid=b9b676a0-1f19-4aaf-807d-e712d7758b64&algo_exp_id=b9b676a0-1f19-4aaf-807d-e712d7758b64-1&pdp_npi=4%40dis%21EUR%2116.48%2116.48%21%21%2117.45%21%21%402103209b17017550135711815e8815%2112000033106113757%21sea%21IT%210%21AB&curPageLogUid=SzqEk2lL0gTd)<br>

## Compatible USB Cables?
![TypeC/MicroUSB](cable.png)<br>*USB Type-C/Micro USB*<br>
![TypeC/MicroUSB](cable2.png)<br>*USB Type-C/Micro USB*<br>

- # 2. Device Preparation <div id="preparazione"></div>
**1 - Run the bash in order to make a new daemon**<br>
- `sudo bash install.sh`

- # 3. System Configuration <div id="configurazione"></div>
**1 - Open "configuration" file and fill the empty values with yours:** <br>
```
{
    "receiverNumber": "",
    "localSMSC": "",
    "apn": "",
    "dbPath": "/home/pi/data/generalDB.db",
    "minDistance": 50,
    "keyTextMessage": "007",  
    "logPath": "/home/pi/piHat/logs/gps.log",
    "powerPin": 4,
    "timer_keep_send_message": 600,
    "timer": 60,
    "timer_sync_ntp": 150,
    "videoPath": "/home/pi/Videos/",
    "minRunDistance": 100,
    "pinNumber": 17
}
```

- # **4. Pros & Cons** <div id="pros-and-cons"></div>
| **Pros**                                      | **Cons**                                                |
|-----------------------------------------------|----------------------------------------------------------|
| Wide coverage                                 | Limited bandwidth                                        |
| Low power consumption                         | Limited transmission speed                               |
| Obstacle penetration                          | Interference                                             |
| Reduced costs                                 | Security concerns                                        |
| Application versatility                       | Data packet limitations                                  | 

- # **5. Curiosities** <div id="curiosities"></div>
1. LoRa utilizes sub-gigahertz radio frequency bands such as 433 MHz, 868 MHz (Europe), and 915 MHz (North America).
2. It ensures long-range transmissions (over 10 km in rural areas, 3–5 km in highly urbanized zones) with low power consumption.
3. It consists of two parts: LoRa, the physical layer, and LoRaWAN (Long Range Wide Area Network), the upper layers.
4. New LoRa chipsets feature reduced power consumption, increased transmission power, and smaller sizes compared to previous generations.
5. It offers geolocation capabilities to triangulate device positions using timestamps from gateways.
6. Provides long-range connectivity for Internet of Things (IoT) devices across various sectors.
7. Reference to [AT Command User Manual](https://resource.heltec.cn/download/CubeCell/AT_Command_list/CubeCell_Series_AT_Command_User_Manual_V0.4.pdf)
8. Reference to [Understanding LoRa](https://development.libelium.com/lora_networking_guide/understanding-lora)

- # **6. Support** <div id="support"></div>
For any questions, bug reports, or feature requests, please open a new issue in our GitHub repository. We will strive to respond as quickly as possible.
For more urgent inquiries or other issues, you can contact us via email at davide.polli@dedem.it. Please include complete details about the encountered problem for a faster resolution.
We are committed to continually improving the application and value every contribution and feedback from our community.

