import json
import collections
from colour import Color


class Layout(object):
    """The representation is:
    beacon: index of the beacon
    row: row in the beacon, starting from bottom
    side: side of the beacon, 0 based
    """

    options = {
        'map_file': 'prmd/maps/map0_fixed.json',
        'beacons': 2,
        'rows': 9,
        'sides': 4,
        'total_leds': 512
    }

    led_map = [
        # {
        #     'all': [],
        #     'all_rows': [],
        #     'all_sides': [],
        #     'map': []
        # }, ...
    ]

    _off = Color(rgb=(0, 0, 0))

    def __init__(self, options=None):
        self.options.update(options or {})
        self._create_led_map()
        self.all(self._off)  # set everything to off

    def flatten(self, l):
        for el in l:
            if (isinstance(el, collections.Iterable) and
                    not isinstance(el, basestring)):
                for sub in self.flatten(el):
                    yield sub
            else:
                yield el

    def _create_led_map(self):
        with open(self.options['map_file']) as mf:
            strct = json.load(mf)['structure']
            for beacon in range(len(strct)):
                self.led_map.append({
                    'all': [],
                    'all_rows': [],
                    'all_sides': [[], [], [], []],  # 4 side hardcoded
                    'map': []
                })
                self.led_map[beacon]['map'] = strct[beacon]
                self.led_map[beacon]['all'] = list(self.flatten(strct[beacon]))
                for row in strct[beacon]:
                    self.led_map[beacon]['all_rows'].append(
                        list(self.flatten(row))
                    )
                    for sid in range(len(row)):
                        self.led_map[beacon]['all_sides'][sid] += row[sid]

    def get_output(self):
        return self.current_colors

    def color_to_rgb(self, color):
        return tuple(int(i * 255) for i in color.rgb)

    def all(self, color):
        self.current_colors = (
            [self.color_to_rgb(color)] * self.options['total_leds']
        )

    def fade_all(self, decay=0.01):
        pass

    def set_beacon(self, beacon, color):
        self.set_pixels(self.led_map[beacon]['all'], self.color_to_rgb(color))

    def set_side(self, side, color, beacon=None):
        if beacon is not None:
            beacon = [beacon]
        else:
            beacon = range(self.options['beacons'])

        for b in beacon:
            self.set_pixels(
                self.led_map[b]['all_sides'][side], self.color_to_rgb(color)
            )

    def set_row(self, row, color, beacon=None):
        if beacon is not None:
            beacon = [beacon]
        else:
            beacon = range(self.options['beacons'])

        for b in beacon:
            self.set_pixels(
                self.led_map[b]['all_rows'][row], self.color_to_rgb(color)
            )

    def set_pixels(self, pixels, rgb_color):
        for p in pixels:
            self.current_colors[p] = rgb_color
