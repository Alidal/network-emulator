import math
from .constants import REGIONAL_NETWORK_SIZE


class Node:
    def __init__(self, _id, network_id):
        self.id = _id
        self.network_id = network_id
        self.routing_table = {}

        radius = 200
        angle = (self.id - REGIONAL_NETWORK_SIZE * network_id)\
            * int(360 / REGIONAL_NETWORK_SIZE)
        # Some hardcoded values
        center_x = 300 if network_id % 2 == 0 else 1000
        center_y = 300 if network_id < 2 else 800
        self.x = int(center_x + radius * math.sin(math.radians(angle)))
        self.y = int(center_y + radius * math.cos(math.radians(angle)))

    def to_dict(self):
        return {
            'id': self.id,
            'label': self.id,
            'group': self.network_id,
            'x': self.x,
            'y': self.y,
        }

    def __hash__(self):
        return self.id

    def __repr__(self):
        return str(self.id)
