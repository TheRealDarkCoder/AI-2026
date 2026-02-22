import random
from IPython.display import clear_output
import time

class Node:
    """
    Represents a node in the grid.
    """
    def __init__(self, grid, coords, carrying_key, goal=False, initial=False, blocked=False):
        self.coords = coords # coordinates represented as (x, y)
        self.successors = [] # list of Node objects
        self.grid = grid # a reference to the grid where this node is located
        self.parent = None # Node object
        self.action = None # string representing the action taken to reach this node from the parent node
        self.initial = initial # boolean indicating whether this node is the initial state
        self.blocked = blocked # boolean indicating whether this node is blocked
        self.locked = False # boolean indicating whether this node is locked
        self.vertical_door = False # boolean indicating whether this node has a vertical door
        self.horizontal_door = False # boolean indicating whether this node has a horizontal door
        self.has_key = False # boolean indicating whether this node has a key
        self.goal = goal # boolean indicating whether this node is the goal
        self.lava = False # boolean indicating whether this node is lava
        self.trap = False # boolean indicating whether this node is a trap
        self.current = False # boolean indicating whether this node is the current state
        self.id = None # unique integer identifier for each node
        self.carrying_key = carrying_key # boolean indicating whether the agent is carrying a key
    
    def get_neighbor(self, action, carrying_key):
        """
        Returns the neighboring node corresponding to the given action, or None in case of error.
        """
        if action == "up":
            new_coords = (self.coords[0], self.coords[1] + 1)
        elif action == "left":
            new_coords = (self.coords[0] - 1, self.coords[1])
        elif action == "down":
            new_coords = (self.coords[0], self.coords[1] - 1)
        elif action == "right":
            new_coords = (self.coords[0] + 1, self.coords[1])
        elif action == "random":
            new_coords = [(self.coords[0], self.coords[1] + 1), (self.coords[0] - 1, self.coords[1]), (self.coords[0], self.coords[1] - 1), (self.coords[0] + 1, self.coords[1])]
            new_coords = random.choice(new_coords)
        else:
            raise ValueError("Invalid action. Use 'up', 'left', 'down', or 'right'.")
        if (0 <= new_coords[0] < self.grid.xlim and 0 <= new_coords[1] < self.grid.ylim):
            try:
                if carrying_key:
                    neighbor = self.grid.nodes2[self.grid.ylim-1-new_coords[1]][new_coords[0]]  # invert y to match Cartesian coordinates
                    return neighbor
                else:
                    neighbor = self.grid.nodes[self.grid.ylim-1-new_coords[1]][new_coords[0]]  # invert y to match Cartesian coordinates
                    return neighbor
            except IndexError:
                return None
        return None
    
    def reset(self):
        """
        Resets the node's properties to their initial state.
        """
        self.successors = []
        self.parent = None
        self.current = False
        if self.initial:
            self.current = True
        self.action = None
        if self.trap:
            self.lava = False
        if self.vertical_door or self.horizontal_door:
            self.locked = True

    def goal_test(self):
        """
        Checks if the current node is a goal state.
        Returns True if the node is a goal state, False otherwise.
        """
        return self.goal  
    
    def __str__(self):
        return f"Node(coords={self.coords}, parent={self.parent.coords if self.parent else None}, successors={[s.coords for s in self.successors]}, initial={self.initial}, goal={self.goal})"
    
class Grid:
    """
    Represents a grid of nodes where the search will take place."""
    def __init__(self, xlim=35, ylim=21):
        self.nodes = [] # list of nodes in the grid
        self.nodes2 = []  # list of nodes in the second grid
        self.nodes_dict = {}  # dictionary to map coordinates to nodes
        self.nodes2_dict = {}  # dictionary to map coordinates to nodes in the second grid
        self.xlim = xlim
        self.ylim = ylim
        self.search_visualization = True
        self.search_delay = 0.1
        self.node_count = 0
        self.key_square = None

    def generate_nodes(self, carrying_key):
        """
        Generates a fixed grid of nodes with specific properties.
        """
        for y in range(self.ylim):
            row = []
            for x in range(self.xlim):
                node = Node(self, (x, (self.ylim-1)-y), carrying_key)  # invert y to match Cartesian coordinates
                if (node.coords[0] == 2 and node.coords[1] == 9 and not carrying_key):
                    node.initial = True
                    node.current = True
                if ( # walls
                    (node.coords[0] == 4 and node.coords[1] >= 3) or 
                    (node.coords[1] == 6 and node.coords[0] >= 5 and node.coords[0] <= 12) or
                    (node.coords[0] == 0) or (node.coords[0] == self.xlim - 3 and node.coords[1] >= 3 and node.coords[1] != 8) or
                    (node.coords[0] == self.xlim - 1) or
                    (node.coords[1] == 0) or (node.coords[1] == self.ylim - 1) or
                    (node.coords[1] == 2 and node.coords[0] != 2 and node.coords[0] <= 12) or
                    (node.coords[0] == 8 and node.coords[1] >= 7)
                ):
                    node.blocked = True
                if (
                    (node.coords[0] == 4 and node.coords[1] == 4)
                ):
                    node.vertical_door = True
                    node.blocked = False
                    node.locked = True
                if (
                    (node.coords[0] == 6 and node.coords[1] == 6) or
                    (node.coords[0] == 10 and node.coords[1] == 6)
                ):
                    node.horizontal_door = True
                    node.blocked = False
                    node.locked = True
                if (node.coords[0] == 10 and node.coords[1] == 10):
                    node.goal = True
                    node.blocked = False
                if (node.coords[0] == 1 and node.coords[1] == 1 and not carrying_key):
                    node.has_key = True
                    self.key_square = node
                if (node.coords[0] >= 5 and node.coords[0] <= 7 and node.coords[1] >= 7 and node.coords[1] <= 9):
                    node.lava = True
                if (
                    (node.coords[0] == 6 and node.coords[1] == 4) or
                    (node.coords[0] == 8 and node.coords[1] == 5) or
                    (node.coords[0] == 8 and node.coords[1] == 3) or
                    (node.coords[0] == 10 and node.coords[1] == 4)
                ):
                    node.trap = True
                self.node_count += 1
                node.id = self.node_count
                row.append(node)
            if not carrying_key:
                self.nodes.append(row)
                self.nodes_dict.update({node.coords: node for node in row})
            else:
                self.nodes2.append(row)
                self.nodes2_dict.update({node.coords: node for node in row})

    def get_initial(self):
        """
        Returns the initial node in the grid.
        If no initial node is found, returns None.
        """
        for row in self.nodes:
            for node in row:
                if node.initial:
                    return node
        return None

    def reset(self):
        """
        Resets the grid to its initial state by resetting all nodes and the expansion count.
        """
        for row in self.nodes:
            for node in row:
                if node == self.key_square:
                    node.has_key = True
                node.reset()
        for row in self.nodes2:
            for node in row:
                node.reset()
        self.expansions = 0

    def visualize(self, agent, delay=0):
        """
        Visualizes the current state of the grid with print statements.
        """
        clear_output(wait=True)
        if agent is not None and agent.has_key:
            for row in self.nodes2:
                print(" ".join("@" if node.current else "G" if node.goal else  "|" if node.vertical_door else "—" if node.horizontal_door else "■" if node.blocked else "K" if node.has_key else "~" if node.lava else "T" if node.trap else "." for node in row))
        else:
            for row in self.nodes:
                print(" ".join("@" if node.current else "G" if node.goal else  "|" if node.vertical_door else "—" if node.horizontal_door else "■" if node.blocked else "K" if node.has_key else "~" if node.lava else "T" if node.trap else "." for node in row))
        time.sleep(delay)