from random import randint, choice
from .regional import RegionalNetwork
from .connection import Connection
from .constants import REGIONAL_NETWORKS_NUMBER, REGIONAL_NETWORK_SIZE,\
    AVERAGE_NODE_POWER, POSSIBLE_WEIGHTS


class GlobalNetwork():
    def __init__(self):
        connections_number = self.generate_random_connection_number()
        self.regional_nets = [RegionalNetwork(i * REGIONAL_NETWORK_SIZE + 1,
                                              REGIONAL_NETWORK_SIZE,
                                              connections_number[i])
                              for i in range(REGIONAL_NETWORKS_NUMBER)]

        # Add connections between regional networks
        self.connections_between_networks = []
        self.add_connection(3, 24)
        self.add_connection(24, 38)
        self.add_connection(38, 19)
        self.add_connection(19, 3)

    def add_connection(self, source, target):
        connection = Connection(choice(POSSIBLE_WEIGHTS), source, target)
        self.connections_between_networks.append(connection)

    def generate_random_connection_number(self):
        """Generate number of connections in regional networks considering
        average node power.
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

    def connections_to_list(self):
        network = []
        for reg_net in self.regional_nets:
            network += reg_net.connections_to_list()
        network += [conn.to_dict() for conn in self.connections_between_networks]
        return network

    def nodes_to_list(self):
        nodes = []
        for reg_net in self.regional_nets:
            nodes += reg_net.nodes_to_list()
        return nodes
