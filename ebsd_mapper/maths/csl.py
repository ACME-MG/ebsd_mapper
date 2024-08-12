"""
 Title:         Coincidence Site Lattice (CSL)
 Description:   For generating euler angles that satisfy CSL criteria
 Referennces:   http://pajarito.materials.cmu.edu/lectures/L14-CSL_Theory_GBE-17Mar16.pdf
                https://github.com/heprom/pymicro/blob/master/pymicro/crystal/microstructure.py
 Author:        Janzen Choi

"""

# Libraries
import numpy as np

def get_symmetry_matrices(type:str="cubic") -> list:
    """
    Returns the symmetry matrices

    Parameters:
    * `type`: The crystal structure type

    Returns a list of the symmetry matrices given the type
    """
    if type == "cubic":
        return get_cubic_symmetry_matrices()
    elif type == "hexagonal":
        return get_hexagonal_symmetry_matrices()
    elif type == "tetrahedral":
        return get_tetrahedral_symmetry_matrices()

def get_cubic_symmetry_matrices() -> list:
    """
    Returns a list of cubic symmetry matrices
    """
    return [
        [[1,0,0],  [0,1,0],  [0,0,1]],
        [[0,0,1],  [1,0,0],  [0,1,0]],
        [[0,1,0],  [0,0,1],  [1,0,0]],
        [[0,-1,0], [0,0,1],  [-1,0,0]],
        [[0,-1,0], [0,0,-1], [1,0,0]],
        [[0,1,0],  [0,0,-1], [-1,0,0]],
        [[0,0,-1], [1,0,0],  [0,-1,0]],
        [[0,0,-1], [-1,0,0], [0,1,0]],
        [[0,0,1],  [-1,0,0], [0,-1,0]],
        [[-1,0,0], [0,1,0],  [0,0,-1]],
        [[-1,0,0], [0,-1,0], [0,0,1]],
        [[1,0,0],  [0,-1,0], [0,0,-1]],
        [[0,0,-1], [0,-1,0], [-1,0,0]],
        [[0,0,1],  [0,-1,0], [1,0,0]],
        [[0,0,1],  [0,1,0],  [-1,0,0]],
        [[0,0,-1], [0,1,0],  [1,0,0]],
        [[-1,0,0], [0,0,-1], [0,-1,0]],
        [[1,0,0],  [0,0,-1], [0,1,0]],
        [[1,0,0],  [0,0,1],  [0,-1,0]],
        [[-1,0,0], [0,0,1],  [0,1,0]],
        [[0,-1,0], [-1,0,0], [0,0,-1]],
        [[0,1,0],  [-1,0,0], [0,0,1]],
        [[0,1,0],  [1,0,0],  [0,0,-1]],
        [[0,-1,0], [1,0,0],  [0,0,1]],
    ]

def get_hexagonal_symmetry_matrices() -> list:
    """
    Returns the hexagonal symmetry matrices
    """
    a = (3 ** 0.5) / 2
    return [
        [[1,0,0],     [0,1,0],     [0,0,1]],
        [[-0.5,a,0],  [-a,-0.5,0], [0,0,1]],
        [[-0.5,-a,0], [a,-0.5,0],  [0,0,1]],
        [[0.5,a,0],   [-a,0.5,0],  [0,0,1]],
        [[-1,0,0],    [0,-1,0],    [0,0,1]],
        [[0.5,-a,0],  [a,0.5,0],   [0,0,1]],
        [[-0.5,-a,0], [-a,0.5,0],  [0,0,-1]],
        [[1,0,0],     [0,-1,0],    [0,0,-1]],
        [[-0.5,a,0],  [a,0.5,0],   [0,0,-1]],
        [[0.5,a,0],   [a,-0.5,0],  [0,0,-1]],
        [[-1,0,0],    [0,1,0],     [0,0,-1]],
        [[0.5,-a,0],  [-a,-0.5,0], [0,0,-1]],
    ]

def get_tetrahedral_symmetry_matrices() -> list:
    """
    Returns the tetrahedral symmetry matrices
    """
    return [
        [[1,0,0],  [0,1,0],  [0,0,1]],
        [[-1,0,0], [0,1,0],  [0,0,-1]],
        [[1,0,0],  [0,-1,0], [0,0,-1]],
        [[-1,0,0], [0,-1,0], [0,0,1]],
        [[0,1,0],  [-1,0,0], [0,0,1]],
        [[0,-1,0], [1,0,0],  [0,0,1]],
        [[0,1,0],  [1,0,0],  [0,0,-1]],
        [[0,-1,0], [-1,0,0], [0,0,-1]],
    ]
