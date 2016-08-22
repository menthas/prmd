
class BaseViz(object):
    # a dict of things that can be configured using this visualization
    config_def = {}
    # whether this visualization is active or not
    active = False
    # name of the visualizer for display purposes
    name = 'BaseViz###'

    LEFT_BEACON = 0
    RIGHT_BEACON = 1

    def __init__(self, container):
        self.container = container
        self.layout = container.layout
        self.config = [{}, {}]
        for key in self.config_def:
            self.config[self.LEFT_BEACON][key] = self.config_def[key]['value']
            self.config[self.RIGHT_BEACON][key] = self.config_def[key]['value']

    def visualize(self, data, time_diff=None):
        raise NotImplemented

    def update_config(self, data):
        for key in self.config_def:
            if key in data:
                self.config[data[key]['beacon']][key] = data[key]['value']

    def console_viz(self, data, feature='tone'):
        if feature == 'tone':
            print(
                ('*' if data['tone'] > 0 else '-') *
                int(abs(data['tone'] * 300))
            )
        elif feature == 'beat':
            print(
                ('*' if data['is_beat'] else '') * 100
            )
        elif feature == 'onset':
            print(
                ('*' if data['onset'] else '') * 100
            )
        elif feature == 'energy':
            print(
                '*' * (data['energy'] / 100)
            )
        else:
            print('Feature not supported')
