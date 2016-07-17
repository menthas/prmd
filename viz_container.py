import redis
import ujson as json

from layout import Layout
from visualizations.flat import FlatViz
from lib import opc


class VizContainer(object):
    REDIS_CONF_DEF_KEY = 'prmd:active_viz_config_def'
    REDIS_CONF_CHANGED_KEY = 'prmd:config_changed'
    REDIS_CONF_VALUE_KEY = 'prmd:config_value'
    REDIS_LAYOUT_KEY = 'prmd:layout'
    REDIS_VIZ_LIST = 'prmd:viz_list'

    active_viz = None
    use_redis = True
    use_fadecandy = True

    FADECANDY_SERVER = 'localhost:7890'

    def __init__(self, audio_input):
        self.layout = Layout()
        self.audio_input = audio_input
        if self.use_redis:
            self.redis = redis.StrictRedis()
        if self.use_fadecandy:
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
            FlatViz(self.layout)
        ]
        if self.use_redis:
            self.redis.rpush(
                self.REDIS_VIZ_LIST, *[v.name for v in self.visualizations]
            )

    def config_reader(self, data, time_diff=None):
        if not self.use_redis:
            return
        changed = self.redis.getset(self.REDIS_CONF_CHANGED_KEY, "0")
        if changed == "1":
            config = json.reads(self.redis.get(self.REDIS_CONF_VALUE_KEY))
            self.visualizations[self.active_viz].config = config

    def layout_handler(self, data, time_diff=None):
        if self.use_fadecandy:
            self.fc_client.put_pixels(self.layout.current_colors)
        if self.use_redis:
            layout = json.dumps(self.layout.current_colors)
            self.redis.set(self.REDIS_LAYOUT_KEY, layout)

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
