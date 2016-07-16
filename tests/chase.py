#!/usr/bin/env python
import time
import random
import sys
sys.path.append('/home/menthas/dev/prmd')

from lib import opc  # NOQA

numLEDs = 5
client = opc.Client('localhost:7890')

while True:
    color = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )
    for i in range(numLEDs):
        pixels = [(0, 0, 0)] * numLEDs
        pixels[i] = color
        client.put_pixels(pixels)
        time.sleep(1)
