import sys
import math
import heapq
from random import randint, choice
from .node import Node
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
        temp_gateways = (2, 18, 23, 37)
        self.gateways = {i + 1: self.nodes[temp_gateways[i]] for i in range(4)}
        self.add_connection(2, 23)
        self.add_connection(23, 37)
        self.add_connection(37, 18)
        self.add_connection(18, 2, recalc_table=True)

    def recalculate_routing_tables(self):
        for node_id in self.nodes:
            self.nodes[node_id].routing_table = self.generate_routing_table(node_id)

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
                                         max_connections / 2.5)
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

    def generate_routing_table(self, node_id):
        table = {}
        for target in self.nodes.values():
            table[target.id] = {}
            table[target.id]['min_weights'] = self.shortest_path(node_id, target.id)
            table[target.id]['min_transitions'] = self.shortest_path(node_id, target.id, no_weight=True)
        del table[node_id]
        return table

    def shortest_path(self, start, finish, no_weight=False):
        distances = {}  # Distance from start to node
        previous = {}  # Previous node in optimal path from source
        nodes = []  # Priority queue of all nodes in Graph

        for node_id in self.nodes:
            if node_id == start:  # Set root node as distance of 0
                distances[node_id] = 0
                heapq.heappush(nodes, [0, node_id])
            else:
                distances[node_id] = sys.maxsize
                heapq.heappush(nodes, [sys.maxsize, node_id])
            previous[node_id] = None

        while nodes:
            smallest = heapq.heappop(nodes)[1]  # node in nodes with smallest distance in distances
            if smallest == finish:  # If the closest node is our target we're done so print the path
                path = []
                while previous[smallest]:  # Traverse through nodes til we reach the root which is 0
                    path.append(smallest)
                    smallest = previous[smallest]
                return {
                    'path': [start] + path[::-1],
                    'cost': distances[finish]
                }
            if distances[smallest] == sys.maxsize:  # All remaining vertices are inaccessible from source
                break

            neighbors = self.get_node_connections(smallest)
            for neighbor, weight in neighbors.items():  # Look at all the nodes that this node is attached to
                # For unweighted graph
                if no_weight:
                    weight = 1
                alt = distances[smallest] + weight  # Alternative path distance
                if alt < distances[neighbor]:  # If there is a new shortest path update our priority queue (relax)
                    distances[neighbor] = alt
                    previous[neighbor] = smallest
                    for n in nodes:
                        if n[1] == neighbor:
                            n[0] = alt
                            break
                    heapq.heapify(nodes)

    def datagram_mode(self, start, finish, message_length, package_size, **kwargs):
        package_size = int(package_size)
        pathes = []

        def build_pathes(cur_path):
            if cur_path[-1] == finish:
                pathes.append(cur_path)
                return

            routing_table = self.nodes[cur_path[-1]].routing_table[finish]
            next = routing_table['min_weights']['path'][1]
            if next not in cur_path:
                build_pathes(cur_path + [next])
                if routing_table['min_weights']['path'] != routing_table['min_transitions']['path']:
                    build_pathes(cur_path + [routing_table['min_transitions']['path'][1]])

        build_pathes([int(start)])

        start_num_of_data_packages = math.ceil(int(message_length) / int(package_size))
        size_of_service_package = 100
        traffic = 0
        speed = 1000  # Default speed in connection with weight 1
        time = 0
        num_of_data_packages = 0
        for i in range(start_num_of_data_packages):
            path = pathes[i % len(pathes)]
            num_of_data_packages += len(path) - 1
            traffic += package_size + size_of_service_package
            for i in range(len(path) - 1):
                conn = self.get_connection_between(path[i], path[i + 1])
                time += ((package_size + size_of_service_package) / speed) * conn.weight

        return {
            'service_packages': num_of_data_packages,
            'data_packages': num_of_data_packages,
            'time': int(time),
            'path': pathes,
            'traffic': traffic,
            'finish': finish
        }

    def logical_channel_mode(self, start, finish, message_length, package_size, **kwargs):
        routing_table = self.nodes[int(start)].routing_table[int(finish)]['min_weights']
        path = routing_table['path']
        print(path)
        transitions = len(path) - 1

        num_of_data_packages = math.ceil(int(message_length) / int(package_size)) * transitions
        # Connect + disconnect + acks for each package
        num_of_service_packages = (2 + num_of_data_packages) * transitions
        size_of_service_package = 100
        traffic = (num_of_data_packages * int(package_size) + num_of_service_packages\
                   * size_of_service_package) / transitions
        speed = 1000  # Default speed in connection with weight 1
        time = 0
        for i in range(len(path) - 1):
            conn = self.get_connection_between(path[i], path[i+1])
            time += (traffic / speed) * conn.weight

        return {
            'service_packages': num_of_service_packages,
            'data_packages': num_of_data_packages,
            'time': int(time),
            'path': path,
            'traffic': traffic,
            'finish': finish
        }

    def get_node_connections(self, node_id, exclude=None):
        if exclude is None:
            exclude = []
        result = {}
        for conn in self.connections.values():
            if conn.source == node_id and conn.target not in exclude:
                result[conn.target] = conn.weight
            elif conn.target == node_id and conn.source not in exclude:
                result[conn.source] = conn.weight
        return result

    def get_connection_between(self, a, b):
        for conn in self.connections.values():
            if conn.is_connection_between(a, b):
                return conn

        return None

    def add_node(self, node_id, network_id):
        """Just a little shortcut for explicity"""
        self.nodes[node_id] = Node(node_id, network_id)

    def add_connection(self, source, target, network_id=-1, recalc_table=False):
        """Add new connection to global list of connections.
        network_id=-1 means that connection is between regional networks
        """
        possible_types = ('duplex', 'half-duplex')
        connection = Connection(weight=choice(POSSIBLE_WEIGHTS),
                                source=source, target=target,
                                _type=choice(possible_types),
                                network_id=network_id)
        self.connections[connection.id] = connection

        if source not in self.nodes:
            network_id = self.nodes[target].network_id
            self.add_node(source, network_id)
        elif target not in self.nodes:
            network_id = self.nodes[source].network_id
            self.add_node(target, network_id)

        if recalc_table:
            self.recalculate_routing_tables()
        return connection

    def update_connection(self, conn_dict):
        self.connections[conn_dict['id']].update_from_dict(conn_dict)

    def delete_connection(self, conn_id):
        del self.connections[conn_id]
        self.recalculate_routing_tables()

    def delete_node(self, node_id):
        del self.nodes[node_id]
        self.recalculate_routing_tables()

    def serialize_connections(self):
        """Serialize connection objects list to list of dictionaries"""
        return [conn.to_dict() for conn in self.connections.values()]

    def serialize_nodes(self):
        """Serialize list of all nodes in network
        :return: list of nodes with calculated position of each node"""
        return [node.to_dict() for node in self.nodes.values()]
