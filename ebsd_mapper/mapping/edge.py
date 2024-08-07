"""
 Title:         Edge
 Description:   Represents an edge
 Author:        Janzen Choi

"""

# Libraries
import numpy as np

# Edge class
class Edge:

    def __init__(self, node_1:int, node_2:int):
        """
        Constructor for mapped grain object

        Parameters:
        * `node_1`: First node
        * `node_2`: Second node
        """
        self.node_1 = node_1
        self.node_2 = node_2
        self.errors = []

    def get_node_1(self) -> int:
        """
        Returns the first node
        """
        return self.node_1

    def get_node_2(self) -> int:
        """
        Returns the second node
        """
        return self.node_2

    def add_error(self, error:float) -> None:
        """
        Adds an error to contribute to the weight

        Parameters:
        * `error`: The error to be added
        """
        self.errors.append(error)

    def get_errors(self) -> list:
        """
        Returns the errors
        """
        return self.errors

    def get_weight(self) -> float:
        """
        Returns the averaged errors
        """
        return np.average(self.errors)
