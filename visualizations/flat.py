from colour import Color
from base_viz import BaseViz


class FlatViz(BaseViz):
    name = "Single Color"
    config_def = {
        'color': {
            'type': 'color_selector',
            'default': '#FFE300'
        },
        'luminance': {
            'type': 'slider',
            'range': [0, 100],
            'default': 50
        }
    }

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
        color = Color(self.config['color'])
        luminance_factor = (data['tone'] + 1) / 2
        color.luminance = (
            (self.config['luminance'] / 100.0) * luminance_factor
        )
        self.layout.all(color)
        self.console_viz(data, feature='tone')
