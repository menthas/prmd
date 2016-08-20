import redis
import ujson as json

from layout import Layout
from visualizations.flat import FlatViz
from lib import opc


class VizContainer(object):
    REDIS_CONF_DEF_KEY = 'prmd:active_viz_config_def'
    REDIS_CONF_CHANGED_KEY = 'prmd:config_changed'
    REDIS_CONF_VALUE_KEY = 'prmd:config_value'
    REDIS_VIZ_LIST = 'prmd:viz_list'

    active_viz = None
    use_redis = True

    FADECANDY_SERVER = 'localhost:7890'

    LEFT = 0
    RIGHT = 1

    global_config = {
        'left_on': True,
        'left_color': (147 / 255.0, 0 / 255.0, 255 / 255.0),
        'left_lum': 30,
        'left_rows': [1, 1, 1, 1, 1, 1, 1, 1, 1],
        'left_sides': [1, 1, 1, 1],
        'left_spectrum': [1] * 25,

        'right_on': True,
        'right_color': (147 / 255.0, 0 / 255.0, 255 / 255.0),
        'right_lum': 30,
        'right_rows': [1, 1, 1, 1, 1, 1, 1, 1, 1],
        'right_sides': [1, 1, 1, 1],
        'right_spectrum': [1] * 25,
    }

    def __init__(self, audio_input):
        self.layout = Layout()
        self.audio_input = audio_input
        if self.use_redis:
            self.redis = redis.StrictRedis()
        self.fc_client = opc.Client(self.FADECANDY_SERVER)

        # create a list of all visualizations, add new ones here
        self.create_viz_list()

        # event loop: read config, run current viz and save layout
        self.audio_input.register_read_listener(
            self.config_reader
        )
        self.audio_input.register_read_listener(
            self.current_viz
        )
        self.audio_input.register_read_listener(
            self.layout_handler
        )
        self.audio_input.register_read_listener(
            self.print_stats
        )

        # use first visualization as the initial one
        self.activate_viz(0)

    def create_viz_list(self):
        self.visualizations = [
            FlatViz(self)
        ]
        if self.use_redis:
            self.redis.rpush(
                self.REDIS_VIZ_LIST, *[v.name for v in self.visualizations]
            )

    def get_conf(self, name):
        return self.global_config.get(name, None)

    def config_reader(self, data, time_diff=None):
        if not self.use_redis:
            return
        changed = self.redis.getset(self.REDIS_CONF_CHANGED_KEY, "0")
        if changed == "1":
            config = json.loads(self.redis.get(self.REDIS_CONF_VALUE_KEY))
            for key in config['global']:
                if '_rows' in key or '_sides' in key:
                    update = config['global'][key]
                    config['global'][key] = self.global_config[key]
                    config['global'][key][update[0]] = update[1]
            self.global_config.update(config['global'])
            self.visualizations[self.active_viz].update_config(config['viz'])

    def layout_handler(self, data, time_diff=None):
        self._apply_global_config()
        self.fc_client.put_pixels(self.layout.get_output())

    def activate_viz(self, viz_index):
        self.visualizations[viz_index].active = True
        self.active_viz = viz_index

        if self.use_redis:
            config = json.dumps(self.visualizations[viz_index].config_def)
            self.redis.set(self.REDIS_CONF_DEF_KEY, config)

    def current_viz(self, data, time_diff=None):
        if self.active_viz is not None:
            self.visualizations[self.active_viz].visualize(
                data, time_diff=time_diff)

    def start(self):
        self.audio_input.read_loop()

    def print_stats(self, data, time_diff):
        fps = int(1 / time_diff)
        if fps < 24:
            print("############ Low FPS: %s" % fps)

    def _apply_global_config(self):
        if not self.global_config['left_on']:
            self.layout.set_beacon(self.LEFT, self.layout._off)
        if not self.global_config['right_on']:
            self.layout.set_beacon(self.RIGHT, self.layout._off)

        for i, row in enumerate(self.global_config['left_rows']):
            if not row:
                self.layout.set_row(i, self.layout._off, beacon=self.LEFT)
        for i, row in enumerate(self.global_config['right_rows']):
            if not row:
                self.layout.set_row(i, self.layout._off, beacon=self.RIGHT)

        for i, side in enumerate(self.global_config['left_sides']):
            if not side:
                self.layout.set_side(i, self.layout._off, beacon=self.LEFT)
        for i, side in enumerate(self.global_config['right_sides']):
            if not side:
                self.layout.set_side(i, self.layout._off, beacon=self.RIGHT)
