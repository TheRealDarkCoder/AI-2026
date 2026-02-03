class BayesNet:
    """
    A simple representation of a Bayesian Network.
    Contains a list of Variable objects.
    """
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def get_first(self):
        if self.nodes:
            return self.nodes[0]
        else:
            raise IndexError("BayesNet is empty")
        
    def get_rest(self, remove):
        """
        Returns a new BayesNet without the specified node.
        """
        if remove in self.nodes:
            new_bnet = BayesNet()
            for node in self.nodes:
                if node != remove:
                    new_bnet.add_node(node)
            return new_bnet
        else:
            raise ValueError("Node not found")
            
    def is_empty(self):
        return len(self.nodes) == 0

class Variable:
    """
    A variable in a Bayesian Network.
    """
    def __init__(self, name, cpt, parents=None):
        self.name = name
        self.parents = parents
        if parents is None:
            self.cpt = {0: 1-cpt, 1: cpt}
        else:
            self.cpt = {}
            for key, value in cpt.items():
                self.cpt.update({key: {0: 1-value, 1: value}})

