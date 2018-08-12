class Category:
    def __init__(self, identifier, name, rank):
        self.id = identifier
        self.name = name
        self.rank = rank
        self.pools = []

    def add_pool(self, pool):
        self.pools.append(pool)

    def to_json(self):
        """
        Convert to a json string as needed by the app
        @return: str
        """
        return "{{\"id\": {0}, \"name\": \"{1}\", \"rank\": {2}}}".format(self.id, self.name, self.rank)