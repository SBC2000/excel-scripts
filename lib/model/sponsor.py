class Sponsor:
    def __init__(self, identifier, name, uri):
        self.id = identifier
        self.name = name
        self.uri = uri

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return other and self.id == other.id

    def to_json(self):
        """
        Convert to a json string as needed by the app
        @return: str
        """
        return "{{\"sponsorId\": {0}, \"name\": \"{1}\", \"uri\": \"{2}\"}}".format(self.id, self.name, self.uri)
