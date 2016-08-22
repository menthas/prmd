from colour import Color

from base_viz import BaseViz


class CustomViz(BaseViz):
    name = "CustomV"
    config_def = {
        'Luminance': {
            'options': ['--', 'Beat', 'Energy', 'Onset'],
            'value': 'Beat'
        },
        'Side': {
            'options': ['--', 'Beat', 'Energy', 'Onset'],
            'value': 'Onset'
        },
        'Row': {
            'options': ['--', 'Beat', 'Energy', 'Energy (R)', 'Onset'],
            'value': '--'
        },
        'Color': {
            'options': ['--', 'Beat', 'Energy', 'Onset'],
            'value': 'Energy'
        },
    }

    side = [0, 0]
    sides = [[None] * 4, [None] * 4]

    row = [0, 0]
    rows = [[None] * 9, [None] * 9]
    row_decay = 0.005

    fade_off = True
    decay_factor = 0.02

    lum = [None, None]

    color_shift = [0, 0]

    def visualize(self, data, time_diff=None):
        self._visualize_beacon(data, self.LEFT_BEACON)
        self._visualize_beacon(data, self.RIGHT_BEACON)

    def _visualize_beacon(self, data, beacon):
        if beacon == self.LEFT_BEACON:
            prefix = 'left_'
        else:
            prefix = 'right_'

        if not self.is_active_on_spectrum(data, prefix):
            return self.layout.set_beacon(beacon, self.layout._off)

        color = Color(rgb=self.container.get_conf(prefix + 'color'))
        color.luminance = self.container.get_conf(prefix + 'lum') / 100.0
        if self.config[beacon]['Luminance'] == 'Beat':
            color = self.beat_lum(data, color, prefix, beacon)
        elif self.config[beacon]['Luminance'] == 'Energy':
            color = self.energy_lum(data, color, prefix, beacon)
        elif self.config[beacon]['Luminance'] == 'Onset':
            color = self.onset_lum(data, color, prefix, beacon)

        if self.config[beacon]['Color'] == 'Beat':
            color = self.beat_color(data, color, prefix, beacon)
        elif self.config[beacon]['Color'] == 'Energy':
            color = self.energy_color(data, color, prefix, beacon)
        elif self.config[beacon]['Color'] == 'Onset':
            color = self.onset_color(data, color, prefix, beacon)

        if self.config[beacon]['Side'] == 'Beat':
            self.beat_side(data, color, prefix, beacon)
        elif self.config[beacon]['Side'] == 'Energy':
            self.energy_side(data, color, prefix, beacon)
        elif self.config[beacon]['Side'] == 'Onset':
            self.onset_side(data, color, prefix, beacon)
        elif self.config[beacon]['Row'] == 'Beat':
            self.beat_row(data, color, prefix, beacon)
        elif self.config[beacon]['Row'] == 'Energy':
            self.energy_row(data, color, prefix, beacon)
        elif self.config[beacon]['Row'] == 'Energy (R)':
            self.energy_row(data, color, prefix, beacon, reverse=True)
        elif self.config[beacon]['Row'] == 'Onset':
            self.onset_row(data, color, prefix, beacon)
        else:
            self.layout.set_beacon(beacon, color)

    def is_active_on_spectrum(self, data, prefix):
        for i, value in enumerate(
                self.container.get_conf(prefix + 'spectrum')):
            active = value > 0.5
            if i / 20.0 <= data['pitch_norm'] <= (i + 1) / 20.0 and active:
                return True
        return False

    def beat_side(self, data, color, prefix, beacon):
        old_side = None
        if data['is_beat']:
            old_side = self.side[beacon]
            self.side[beacon] = (self.side[beacon] + 1) % 4
        self.layout.set_side(self.side[beacon], color, beacon=beacon)
        self.sides[beacon][self.side[beacon]] = color

        if not self.fade_off and old_side is not None:
            self.layout.set_side(old_side, self.layout._off, beacon=beacon)
        elif self.fade_off:
            for side, side_color in enumerate(self.sides[beacon]):
                if side_color is None:
                    continue
                side_color.luminance = max(
                    0, side_color.luminance - self.decay_factor)
                if side_color.luminance < 0.01:
                    self.sides[beacon][side] = None
                    self.layout.set_side(side, self.layout._off, beacon=beacon)
                else:
                    self.layout.set_side(side, side_color, beacon=beacon)

    def beat_row(self, data, color, prefix, beacon):
        old_row = None
        if data['is_beat']:
            old_row = self.row[beacon]
            self.row[beacon] = (self.row[beacon] + 1) % 9
        self.layout.set_row(self.row[beacon], color, beacon=beacon)
        self.rows[beacon][self.row[beacon]] = color

        if not self.fade_off and old_row is not None:
            self.layout.set_row(old_row, self.layout._off, beacon=beacon)
        elif self.fade_off:
            for row, row_color in enumerate(self.rows[beacon]):
                if row_color is None:
                    continue
                row_color.luminance = max(
                    0, row_color.luminance - self.row_decay)
                if row_color.luminance < 0.01:
                    self.rows[beacon][row] = None
                    self.layout.set_row(row, self.layout._off, beacon=beacon)
                else:
                    self.layout.set_row(row, row_color, beacon=beacon)

    def beat_lum(self, data, color, prefix, beacon):
        if self.lum[beacon] is None or (
                self.lum[beacon] < 0.01 and data['is_beat']):
            self.lum[beacon] = self.container.get_conf(prefix + 'lum') / 100.0
        if data['is_beat']:
            color.luminance = min(1, self.lum[beacon] * 1.3)
        else:
            color.luminance = max(0, self.lum[beacon] - self.decay_factor)
        self.lum[beacon] = color.luminance
        return color

    def beat_color(self, data, color, prefix, beacon):
        if data['is_beat']:
            self.color_shift[beacon] = 0.3
        else:
            self.color_shift[beacon] = max(0, self.color_shift[beacon] - 0.005)
        hue = color.hue + self.color_shift[beacon]
        if hue > 1:
            hue = hue - 1
        color.hue = hue
        return color

    def energy_lum(self, data, color, prefix, beacon):
        color.luminance = (
            (self.container.get_conf(prefix + 'lum') / 100.0) *
            data['energy_norm']
        )
        return color

    def energy_row(self, data, color, prefix, beacon, reverse=False):
        rows = int(round(data['energy_norm'] * 9))
        for row in range(rows):
            row_id = 8 - row if reverse else row
            self.layout.set_row(row_id, color, beacon=beacon)
            self.rows[beacon][row_id] = color

        if not self.fade_off and rows < 9:
            r = range(8 - rows) if reverse else range(rows - 1, 9)
            for i in r:
                self.layout.set_row(i, self.layout._off, beacon=beacon)
        elif self.fade_off:
            for row, row_color in enumerate(self.rows[beacon]):
                if row_color is None:
                    continue
                row_color.luminance = max(
                    0, row_color.luminance - self.row_decay)
                if row_color.luminance < 0.01:
                    self.rows[beacon][row] = None
                    self.layout.set_row(row, self.layout._off, beacon=beacon)
                else:
                    self.layout.set_row(row, row_color, beacon=beacon)

    def energy_side(self, data, color, prefix, beacon):
        rgb_color = self.layout.color_to_rgb(color)
        self.layout.set_beacon(beacon, self.layout._off)
        for row in self.layout.led_map[beacon]['map']:
            for side in row:
                side_len = len(side)
                side_on_count = int(round(data['energy_norm'] * side_len))
                side_off = int(round((side_len - side_on_count) / 2.0))
                side_on = side[
                    side_off:(side_on_count + side_off)
                ]
                self.layout.set_pixels(side_on, rgb_color)

    def energy_color(self, data, color, prefix, beacon):
        self.color_shift[beacon] = (data['energy_norm'] / 2)
        hue = color.hue + self.color_shift[beacon]
        if hue > 1:
            hue = hue - 1
        color.hue = hue
        return color

    def onset_row(self, data, color, prefix, beacon):
        old_row = None
        if data['onset']:
            old_row = self.row[beacon]
            self.row[beacon] = (self.row[beacon] + 1) % 9
        self.layout.set_row(self.row[beacon], color, beacon=beacon)
        self.rows[beacon][self.row[beacon]] = color

        if not self.fade_off and old_row is not None:
            self.layout.set_row(old_row, self.layout._off, beacon=beacon)
        elif self.fade_off:
            for row, row_color in enumerate(self.rows[beacon]):
                if row_color is None:
                    continue
                row_color.luminance = max(
                    0, row_color.luminance - self.row_decay)
                if row_color.luminance < 0.01:
                    self.rows[beacon][row] = None
                    self.layout.set_row(row, self.layout._off, beacon=beacon)
                else:
                    self.layout.set_row(row, row_color, beacon=beacon)

    def onset_side(self, data, color, prefix, beacon):
        old_side = None
        if data['onset']:
            old_side = self.side[beacon]
            self.side[beacon] = (self.side[beacon] + 1) % 4
        self.layout.set_side(self.side[beacon], color, beacon=beacon)
        self.sides[beacon][self.side[beacon]] = color

        if not self.fade_off and old_side is not None:
            self.layout.set_side(old_side, self.layout._off, beacon=beacon)
        elif self.fade_off:
            for side, side_color in enumerate(self.sides[beacon]):
                if side_color is None:
                    continue
                side_color.luminance = max(
                    0, side_color.luminance - self.decay_factor)
                if side_color.luminance < 0.01:
                    self.sides[beacon][side] = None
                    self.layout.set_side(side, self.layout._off, beacon=beacon)
                else:
                    self.layout.set_side(side, side_color, beacon=beacon)

    def onset_lum(self, data, color, prefix, beacon):
        if self.lum[beacon] is None or (
                self.lum[beacon] < 0.01 and data['onset']):
            self.lum[beacon] = self.container.get_conf(prefix + 'lum') / 100.0
        if data['onset']:
            color.luminance = min(1, self.lum[beacon] * 1.3)
        else:
            color.luminance = max(0, self.lum[beacon] - self.decay_factor)
        self.lum[beacon] = color.luminance
        return color

    def onset_color(self, data, color, prefix, beacon):
        if data['onset']:
            self.color_shift[beacon] = 0.3
        else:
            self.color_shift[beacon] = max(0, self.color_shift[beacon] - 0.005)
        hue = color.hue + self.color_shift[beacon]
        if hue > 1:
            hue = hue - 1
        color.hue = hue
        return color
