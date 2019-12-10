from pymmh3 import hash_bytes


class Product(object):

    def __init__(self, name, frequency):
        self.id = hash_bytes(name)
        self.name = name
        self.frequency = frequency
        self.depth = None
        self.children = []
        self.parents = []
        self.primary_parent = None

    def calculate_depth(self, path=None):
        if self.depth is not None:
            return self.depth

        path = path or []
        if self.id in path:
            self.depth = 0
            return -1
        path.append(self.id)

        depth = 0
        if self.primary_parent:
            depth = self.primary_parent.calculate_depth(path) + 1

        self.depth = depth
        return depth
