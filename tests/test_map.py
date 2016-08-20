#!/usr/bin/env python
import json
import sys
import collections
sys.path.append('/home/menthas/dev/prmd')

from lib import opc  # NOQA


def flatten(l):
    for el in l:
        if (isinstance(el, collections.Iterable) and
                not isinstance(el, basestring)):
            for sub in flatten(el):
                yield sub
        else:
            yield el

with open('../maps/map0_fixed.json') as data_file:
    data = json.load(data_file)
    structure = data['structure']
    empty = data['empty']

client = opc.Client('localhost:7890')
numLEDs = 512
while True:
    colors = [(0, 0, 0)] * numLEDs
    command = raw_input('[beacon] [row] [side]: ')
    if command.strip() == "":
        client.put_pixels(colors, channel=0)
        continue
    command = command.split(" ")

    if len(command) == 1:
        beacon = int(command[0])
        for i in flatten(structure[beacon]):
            colors[i] = (255, 255, 255)

    if len(command) == 2:
        beacon = int(command[0])
        row = int(command[1])
        for i in flatten(structure[beacon][row]):
            colors[i] = (255, 255, 255)
    if len(command) == 3:
        beacon = int(command[0])
        row = int(command[1])
        side = int(command[2])
        if row >= 0:
            for i in flatten(structure[beacon][row][side]):
                colors[i] = (255, 255, 255)
        else:
            for k in range(9):
                for i in flatten(structure[beacon][k][side]):
                    colors[i] = (255, 255, 255)

    client.put_pixels(colors, channel=0)
