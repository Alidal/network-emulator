import math
from random import randint, choice
from .connection import Connection
from .constants import REGIONAL_NETWORKS_NUMBER, REGIONAL_NETWORK_SIZE,\
    AVERAGE_NODE_POWER, POSSIBLE_WEIGHTS


class GlobalNetwork():
    def __init__(self):
        self.connections = {}
        self.nodes = {}
        connections_number = self.spread_connections()
        for i in range(REGIONAL_NETWORKS_NUMBER):
            self.init_random_regional_network(sum(connections_number[:i+1]),
                                              i*REGIONAL_NETWORK_SIZE + 1, i)

        # Add connections between regional networks
        # EEEE, HARDCODE
        self.add_connection(2, 23)
        self.add_connection(23, 37)
        self.add_connection(37, 18)
        self.add_connection(18, 2)

    def spread_connections(self):
        """Generate number of connections in regional networks considering
        average node power and some other characteristics.
        """
        total_connections_number = int(REGIONAL_NETWORKS_NUMBER *
                                       AVERAGE_NODE_POWER *
                                       REGIONAL_NETWORK_SIZE)
        # Maximum possible number of connections in regional network
        max_connections = REGIONAL_NETWORK_SIZE * (REGIONAL_NETWORK_SIZE - 1)

        result = []
        for _ in range(REGIONAL_NETWORKS_NUMBER - 1):
            num_in_reg_network = randint(REGIONAL_NETWORK_SIZE + 5,
                                         max_connections / 3)
            result.append(num_in_reg_network)
            total_connections_number -= num_in_reg_network
        result.append(total_connections_number)
        return result

    def init_random_regional_network(self, connections_number, start_id,
                                     network_id):
        def get_random_element_id():
            return randint(start_id, start_id + REGIONAL_NETWORK_SIZE - 1)

        def is_connected(source, target):
            return any([conn.is_connection_between(source, target)
                        for conn in self.connections.values()])

        # Generate nodes
        for node_id in range(start_id, start_id + REGIONAL_NETWORK_SIZE):
            self.add_node(node_id, network_id)

        # Get every node at least one connection
        for i in range(start_id, start_id + REGIONAL_NETWORK_SIZE):
            source = target = i
            while source == target or is_connected(source, target):
                target = get_random_element_id()
            self.add_connection(source, target, network_id)

        # Create all other connections between nodes
        while len(self.connections) < connections_number:
            source = get_random_element_id()
            target = get_random_element_id()
            if source != target and not is_connected(source, target):
                self.add_connection(source, target, network_id)

    def add_node(self, node_id, network_id):
        radius = 200
        angle = (node_id - REGIONAL_NETWORK_SIZE * network_id)\
            * int(360 / REGIONAL_NETWORK_SIZE)
        # Some hardcoded values
        x = 300 if network_id % 2 == 0 else 1000
        y = 300 if network_id < 2 else 800
        self.nodes[node_id] = {
            'x': int(x + radius * math.sin(math.radians(angle))),
            'y': int(y + radius * math.cos(math.radians(angle))),
            'id': node_id,
            'label': node_id,
            'group': network_id,
        }

    def add_connection(self, source, target, network_id=-1):
        """Add new connection to global list of connections.
        network_id=-1 means that connection is between regional networks
        """
        connection = Connection(weight=choice(POSSIBLE_WEIGHTS),
                                source=source, target=target,
                                network_id=network_id)
        self.connections[connection.id] = connection

        if source not in self.nodes:
            network_id = self.nodes[target]['group']
            self.add_node(source, network_id)
        elif target not in self.nodes:
            network_id = self.nodes[source]['group']
            self.add_node(target, network_id)

        return connection

    def update_connection(self, conn_dict):
        self.connections[conn_dict['id']].update_from_dict(conn_dict)

    def delete_connection(self, conn_id):
        del self.connections[conn_id]

    def delete_node(self, node_id):
        del self.nodes[node_id]

    def serialize_connections(self):
        """Serialize connection objects list to list of dictionaries"""
        return [conn.to_dict() for conn in self.connections.values()]

    def serialize_nodes(self):
        """Serialize list of all nodes in network
        :return: list of nodes with calculated position of each node"""
        return list(self.nodes.values())
