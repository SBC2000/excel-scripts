class Referee:
    def __init__(self, identifier, name):
        self.id = identifier
        self.name = name

    def get_first_name(self):
        return self.name.split(" ")[0];

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return other and self.id == other.id

    def to_json(self):
        """
        Convert to a json string as needed by the app
        @return: str
        """
        return "{{\"id\": {0}, \"name\": \"{1}\"}}".format(self.id, self.name)
