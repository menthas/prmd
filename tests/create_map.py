#!/usr/bin/env python
import json
import sys
sys.path.append('/home/menthas/dev/prmd')

from lib import opc  # NOQA

data_structure = [
    [  # beacon 1
        [  # row 1
            [   # side one
            ], [], [], []
        ],
        [[], [], [], []],
        [[], [], [], []],
        [[], [], [], []],
        [[], [], [], []],
        [[], [], [], []],
        [[], [], [], []],
        [[], [], [], []],
        [[], [], [], []]
    ],
    [
        [[], [], [], []],
        [[], [], [], []],
        [[], [], [], []],
        [[], [], [], []],
        [[], [], [], []],
        [[], [], [], []],
        [[], [], [], []],
        [[], [], [], []],
        [[], [], [], []]
    ]
]

numLEDs = 512
client = opc.Client('localhost:7890')
beacon = 0
row = 0
side = 0

turned_off = []
i = 0
while i < numLEDs:
    try:
        colors = [(0, 0, 0)] * numLEDs
        colors[i] = (255, 255, 255)
        client.put_pixels(colors, channel=0)
        data = raw_input('[Beacon] [row] [side] id_in_row: ')
        if not data.strip():
            turned_off.append(i)
            i += 1
            continue
        if data == 'print':
            print(json.dumps(data_structure), turned_off)
            continue
        if data == 'back':
            i -= 1
            continue

        info = data.split(' ')
        if len(info) == 4:
            beacon = int(info[0])
            info = info[1:]
        if len(info) == 3:
            row = int(info[0])
            info = info[1:]
        if len(info) == 2:
            side = int(info[0])
            info = info[1:]
        id_in_row = int(info[0])
        data_structure[beacon][row][side].append((id_in_row, i))
        i += 1
    except Exception as e:
        print(e)

print(json.dumps(data_structure), turned_off)
