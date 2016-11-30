import json
import math
import random

from .connection import Connection
from .constants import POSSIBLE_WEIGHTS


def time_sending(shortest_weight, information_length, message_len, delay=0):
    """
    3000 is max length of packet, that can receive element of network
    """
    package_num = math.ceil(float(message_len) / float(information_length))
    result = package_num * shortest_weight
    return result + delay * package_num


class RegionalNetwork:
    def __init__(self, start_id, size, connections_number=0, init_random=True):
        self.size = size
        self.start_id = start_id
        self.connections = []
        # ID of node connected with other regional networks
        self.gateway = self.get_random_element_id()
        if init_random:
            self.init_random_network(connections_number)

    def init_random_network(self, connections_number):
        # Get every node at least one connection
        for i in range(self.start_id, self.start_id + self.size - 1):
            source = target = i
            while source == target or self.is_connected(source, target):
                target = self.get_random_element_id()
            self.add_connection(source, target)

        # Create all other connections between nodes
        while len(self.connections) < connections_number:
            source = self.get_random_element_id()
            target = self.get_random_element_id()
            if source != target and not self.is_connected(source,
                                                          target):
                self.add_connection(source, target)
        # Set number of node that will connect this network to other regional
        # networks
        self.gateway = self.get_random_element_id()

    def get_random_element_id(self):
        return random.randint(self.start_id, self.start_id + self.size - 1)

    def add_connection(self, source, target):
        connection = Connection(random.choice(POSSIBLE_WEIGHTS), source, target)
        self.connections.append(connection)

    def delete_node(self, node_id):
        # Delete all connections from this node
        for i, conn in enumerate(self.connections):
            if conn.source.id == node_id or conn.target.id == node_id:
                del self.connections[i]

    def is_connected(self, source, target):
        return any([conn.is_connection_between(source, target) for conn in self.connections])

    def get_connection_between(self, source, target) -> Connection:
        connection_list = filter(lambda conn: conn.is_connection_between(source,
                                                                         target),
                                 self.connections)
        if connection_list:
            return connection_list[0]
        return None

    def connections_to_list(self):
        return [conn.to_dict() for conn in self.connections]

    def nodes_to_list(self):
        nodes = []
        current_angle = 0
        angle_tick = int(360 / self.size)
        net_num = self.start_id // 10
        x = 300 if net_num % 2 == 0 else 1000
        y = 300 if net_num < 2 else 800
        radius = 200
        for i in range(self.size):
            nodes.append({
                'x': int(x + radius * math.sin(math.radians(current_angle))),
                'y': int(y + radius * math.cos(math.radians(current_angle))),
                'id': self.start_id + i,
                'label': str(self.start_id + i),
                'group': net_num,
            })
            current_angle += angle_tick
        return nodes

    # def table_of_ways(self, id_start):
    #     sequence_sending = self.sequence_sending(id_start)
    #     return {'shortest': shortest_ways_from_sequence(sequence_sending),
    #             'min_transit': min_transit_from_sequence(sequence_sending)}

    # def sequence_sending(self, id_start):
    #     self.about_ways.num_nodes = self.size + 3    # because 3 more gateway nodes
    #     self.about_ways.connections = filter(lambda connection: connection.active, self.connections)
    #     return self.about_ways.sequence_sending(id_start)

    # def send_message(self, id_number, message_len):
    #     header_length = 100
    #     package_length_lst = (1600, 2100, 3100)

    #     send_table_result = []
    #     shortest_table = shortest_ways_from_sequence(self.sequence_sending(id_number))

    #     for pair in shortest_table:
    #         send_table_result.append({'id': pair[0],
    #                                   'logical_connection': map(lambda package_length: (package_length,
    #                                                                                     time_sending(
    #                                                                                         pair[1],
    #                                                                                         package_length - header_length,
    #                                                                                         message_len,
    #                                                                                         delay=4)),
    #                                                             package_length_lst),
    #                                   'datagram_method': map(lambda package_length: (package_length,
    #                                                                                  time_sending(
    #                                                                                      pair[1],
    #                                                                                      package_length - header_length,
    #                                                                                      message_len)),
    #                                                          package_length_lst)})
    #     return {'send_table': send_table_result, 'max_length_packet': 3500}
