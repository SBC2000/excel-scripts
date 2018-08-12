class Pitch:
    def __init__(self, identifier, name, rank):
        self.id = identifier
        self.name = name
        self.rank = rank

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def to_json(self):
        """
        Convert to a json string as needed by the app
        @return: str
        """
        return "{{\"id\": {0}, \"name\": \"{1}\", \"rank\": {2}}}".format(self.id, self.name, self.rank)
