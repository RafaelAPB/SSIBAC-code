class Object:
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

    def __str__(self):
        return self.name

class ObjectSSI:
    def __init__(self, name, decision):
        self.name = name
        self.decision = decision

    def __str__(self):
        return self.name