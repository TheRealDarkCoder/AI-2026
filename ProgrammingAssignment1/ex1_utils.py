from IPython.display import clear_output
import time

class PriorityQueue:
    """
    A simple priority queue implementation using a list.
    Elements are stored as tuples (item, priority) where lower priority values indicate higher priority.
    """
    def __init__(self):
        self.__data = []
    
    def push(self, element, priority):
        """
        Push an element into the priority queue and sort by priority.
        """
        self.__data.append((element, priority))
        self.__data.sort(key=lambda x: x[1])

    def pop(self):
        """
        Pop the element with the highest priority (lowest number) from the queue.
        Returns the item part of the tuple (item, priority).
        If the queue is empty, returns None.
        """
        if len(self.__data) > 0:
            return self.__data.pop(0)[0]
        else:
            return None
    
    def read(self):
        """
        Read the element with the highest priority without removing it from the queue.
        """
        if len(self.__data) > 0:
            return self.__data[0][0]
        else:
            return None

    def is_empty(self):
        """
        Check if the priority queue is empty.
        Returns True if empty, False otherwise.
        """
        return len(self.__data) == 0

class Node:
    """
    Represents a node in the grid.
    """
    def __init__(self, grid, coords=(0, 0), goal=False, initial=False, blocked=False):
        self.coords = coords # coordinates represented as (x, y)
        self.successors = [] # list of Node objects
        self.grid = grid # reference to the grid where this node is located
        self.parent = None #Node object
        self.action = None # string representing the action taken to reach this node from the parent node
        self.initial = initial # boolean indicating whether this node is the initial state
        self.goal = goal # boolean indicating whether this node is a goal state
        self.blocked = blocked # boolean indicating whether this node is blocked
        self.current = False # boolean indicating whether this node is the current state
        self.h = None # heuristic value for this node
        self.g = 0 # path cost

    def expand(self, reached=[]):
        """
        Expands the current node by generating its successors.
        Returns a list of successor nodes that can be reached from the current node.
        Also does internal bookkeeping for returning the path to the goal as well as visualization purposes.
        """
        self.current = True
        self.grid.expansions += 1
        self.grid._reached.add(self)
        directions = [(0, 1), (-1, 0), (0, -1), (1, 0)] # we can move in 4 directions (right, down, left, up)
        for dx, dy in directions:
            if (dx, dy) == (0, 1):
                action = "up"
            elif (dx, dy) == (-1, 0):
                action = "left"
            elif (dx, dy) == (0, -1):
                action = "down"
            elif (dx, dy) == (1, 0):
                action = "right"
            new_coords = [self.coords[0] + dx, self.coords[1] + dy] # move one square in the specified direction
            if (new_coords[0] < self.grid.xlim and new_coords[0] >= 0 and new_coords[1] < self.grid.ylim and new_coords[1] >= 0): # check if the new state is within bounds
                new_node = self.grid.nodes[self.grid.ylim-1-new_coords[1]][new_coords[0]]
                if new_node.parent is None and new_node not in self.grid._reached:
                    new_node.parent = self
                # Make sure the new node is not blocked and ignore the parent node
                if (not new_node.blocked and (new_node.coords != self.parent.coords if self.parent else True)):
                    if not new_node.action:
                        new_node.action = action
                    self.successors.append(new_node)  
   
        if self.grid.search_visualization:
            self.grid.visualize(self.grid.search_delay)
        self.current = False
        return self.successors
    
    def reset(self):
        """
        Resets the node's properties to their initial state.
        """
        self.successors = []
        self.parent = None
        self.current = False
        self.action = None
        self.h = None
        self.g = 0
    
    def goal_test(self):
        """
        Returns True if the node is a goal state, False otherwise.
        """
        return self.goal  
    
    def __str__(self):
        return f"Node(coords={self.coords}, parent={self.parent.coords if self.parent else None}, successors={[s.coords for s in self.successors]}, initial={self.initial}, goal={self.goal})"
    
class Grid:
    """
    Represents a grid of nodes where the search will take place.
    """
    def __init__(self):
        self.nodes = []
        self.expansions = 0
        self.xlim = 40
        self.ylim = 21
        self.search_visualization = False
        self.search_delay = 0.1
        self._reached = set() # internal bookkeeping

    def generate_nodes(self):
        """
        Generates a fixed grid of nodes with specific properties.
        """
        for y in range(self.ylim):
            row = []
            for x in range(self.xlim):
                node = Node(self, (x, (self.ylim-1)-y))  # invert y to match Cartesian coordinates
                # Define goal state:
                if (node.coords[0] == 30 and node.coords[1] == 14):
                    node.goal = True
                # Define initial state:
                elif (node.coords[0] == 10 and node.coords[1] == 12):
                    node.initial = True
                    node.current = True
                # Define blocked nodes:
                elif (
                    (x > 12 and x < 27 and y == 5) or 
                    (x > 12 and x < 27 and y == 11) or
                    (x == 26 and y > 4 and y < 12) or
                    (x == 13 and y == 6) or
                    (x == 13 and y == 10) or
                    (x > 1 and x < 6 and y > 15 and y < 19) or
                    (x > 9 and x < 14 and y > 15 and y < 19) or
                    (x > 17 and x < 22 and y > 15 and y < 19) or
                    (x > 25 and x < 30 and y > 15 and y < 19) or
                    (x > 33 and x < 38 and y > 15 and y < 19) or
                    (x > 1 and x < 6 and y > 15-7 and y < 19-7) or
                    (x > 1 and x < 6 and y > 15-14 and y < 19-14) or
                    (x > 33 and x < 38 and y > 15 and y < 19) or
                    (x > 33 and x < 38 and y > 15-7 and y < 19-7) or
                    (x > 33 and x < 38 and y > 15-14 and y < 19-14)
                ):
                    node.blocked = True
                row.append(node)
            self.nodes.append(row)

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

    def get_goal(self):
        """
        Returns the goal node in the grid.
        If no goal node is found, returns None.
        """
        for row in self.nodes:
            for node in row:
                if node.goal:
                    return node
        return None
    
    def set_search_visualization(self, value):
        """
        Sets whether the search visualization is enabled or not.
        """
        self.search_visualization = value

    def set_search_delay(self, delay):
        """
        Sets the delay for the search visualization.
        """
        self.search_delay = delay

    def reset(self):
        """
        Resets the grid to its initial state by resetting all nodes and the expansion count.
        """
        for row in self.nodes:
            for node in row:
                node.reset()
        self.expansions = 0
        self._reached = set()

    def visualize(self, delay=0):
        """
        Visualizes the current state of the grid with print statements.
        """
        clear_output(wait=True)
        for row in self.nodes:
            print(" ".join("@" if node.current else "S" if node.initial else "G" if node.goal else "■" if node.blocked else "x" if node in self._reached else "." for node in row))
        time.sleep(delay)

