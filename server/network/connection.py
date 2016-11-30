class Connection:
    def __init__(self, weight, source=None, target=None,
                 _type='duplex', satellite=False):
        self.weight = weight * 3 if satellite else weight
        self.type = _type  # 1 is duplex, 1.5 is half-duplex
        self.source = source  # ID of source node
        self.target = target  # ID of target node
        self.satellite = satellite
        self.active = True

    def is_connection_between(self, source, target):
        return {self.source, self.target} == {source, target}

    def to_dict(self):
        return {'from': self.source, 'to': self.target,
                'type': self.type, 'label': self.weight,
                'active': self.active, 'dashes': bool(self.type == 'half-duplex')}
