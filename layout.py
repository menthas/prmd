from colour import Color


class Layout(object):

    # height: 75in
    # base: 20in
    # distance: 2.5in
    # total: 56
    #   ^^ times 2 for the component
    # Note: left and right are defined as you are facing the smaller
    # angle
    default_component = [
        7, 7, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1,  # Left
        7, 7, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1   # Right
    ]

    default_component_count = 4

    _off = Color(rgb=(0, 0, 0))

    def __init__(self, component=None, count=None):
        self.component = component or self.default_component
        self.component_count = count or self.default_component_count
        self.row_count = len(self.component) / 2
        self.all(self._off)  # set everything to off

    def all(self, color):
        self.current_colors = []
        for i in range(self.component_count):
            component = [
                [color.rgb] * i for i in self.component
            ]
            self.current_colors.append(component)
