#phyphox configuration
PP_ADDRESS = "http://172.20.10.1:80"
PP_CHANNELS = ["accX","accY","accZ", "acc_time"]

import requests
import time

while True:
    url = PP_ADDRESS + "/get?" + ("&".join(PP_CHANNELS))
    data = requests.get(url=url).json()

    accX = data["buffer"]['accX']['buffer'][0]
    accY = data["buffer"]['accY']['buffer'][0]
    accZ = data["buffer"]['accZ']['buffer'][0]
    acc_time = data["buffer"]['acc_time']['buffer'][0]
    


    value = [accX, accY, accZ, acc_time]




