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

with open('../maps/map0.json') as data_file:
    data = json.load(data_file)
    structure = data['structure']
    empty = data['empty']

    for beacon in data['structure']:
        for row in beacon:
            for i, side in enumerate(row):
                if not side:
                    continue
                max_id = max([b[0] for b in side]) + 1
                new_side = [0] * max_id
                for item in side:
                    new_side[item[0]] = item[1]
                    if item[1] in data['empty']:
                        data['empty'].remove(item[1])
                row[i] = new_side

    with open('../maps/map0_fixed.json', 'w') as fixed_file:
        fixed_file.write(json.dumps(data, indent=4))
