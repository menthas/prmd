import numpy as np
from colour import Color

from base_viz import BaseViz


class FlatViz(BaseViz):
    name = "FlatV"
    config_def = {}

    side = 0

    def visualize(self, data, time_diff=None):
        """
        data: {
            is_beat: bool,
            onset: bool,
            min_energy: float <<,
            max_energy: float >>,
            tone: signed float (-1, 1)
        }
        """
        old_side = None
        if data['is_beat']:
            old_side = self.side
            self.side = (self.side + 1) % 4
        color = Color(rgb=self.container.get_conf('left_color'))
        luminance_factor = (
            np.sqrt(min(3000, data['left_energy'])) / np.sqrt(3000)
        )
        color.luminance = (
            (self.container.get_conf('left_lum') / 100.0) * luminance_factor
        )
        # self.layout.all(color)
        self.layout.set_side(self.side, color)
        if old_side is not None:
            self.layout.set_side(old_side, self.layout._off)
        # self.console_viz(data, feature='left_energy')
