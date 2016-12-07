class Connection:
    def __init__(self, weight, source=None, target=None, network_id=-1,
                 _type='duplex'):
        self.weight = weight
        self.type = _type  # 1 is duplex, 1.5 is half-duplex
        self.source = source  # ID of source node
        self.target = target  # ID of target node
        self.network_id = network_id

    @property
    def id(self):
        return '{}-{}'.format(self.source, self.target)

    def is_connection_between(self, source, target):
        return {self.source, self.target} == {source, target}

    def to_dict(self):
        return {
            'from': self.source, 'to': self.target, 'id': self.id,
            'dashes': False if self.type == 'duplex' else[2, 2, 10, 10],
            'type': self.type, 'label': self.weight,
        }

    def update_from_dict(self, _dict):
        self.source = _dict['from']
        self.target = _dict['to']
        self.type = _dict['type']
