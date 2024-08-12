"""
 Title:         Reorientation
 Description:   For processing the reorientation trajectories
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
from ebsd_mapper.maths.orientation import euler_to_matrix, matrix_to_euler, get_geodesic, euler_to_quat, quat_to_euler
from ebsd_mapper.maths.csl import get_symmetry_matrices

def get_eq_eulers(euler:list, type:str="cubic") -> list:
    """
    Gets the equivalent euler-bunge angles
    
    Parameters:
    * `euler`: List representing an euler-bunge angle (rads)
    * `type`:  The type of crystal structure
    
    Returns a list of the equivalent euler-bunge angles
    """
    symmetry_matrices = get_symmetry_matrices(type)
    matrix = euler_to_matrix(euler)
    eq_matrices = [np.dot(symmetry_matrix, matrix) for symmetry_matrix in symmetry_matrices]
    eq_eulers = [matrix_to_euler(eq_matrix) for eq_matrix in eq_matrices]
    return eq_eulers

def process_trajectory(trajectory:list) -> list:
    """
    Gets the smoothened reorientation trajectory
    
    Parameters:
    * `trajectory`: The euler-bunge angles (rads)
    
    Returns the smoothened reorientation trajectory
    """
    
    # Force orientations to be the same symmetry
    new_trajectory = [trajectory[0]]
    for euler in trajectory:
        
        # Get latest quaternion and all equivalent quaternions
        eq_eulers = get_eq_eulers(euler)
        eq_quats  = [euler_to_quat(eq_euler) for eq_euler in eq_eulers]
        
        # Select equivalent quaternion closest to the latest quaternion
        latest_quat = euler_to_quat(new_trajectory[-1])
        geodesic_list = [get_geodesic(latest_quat, eq_quat) for eq_quat in eq_quats]
        min_index = geodesic_list.index(min(geodesic_list))
        
        # Add selected equivalent quaternion and repeat
        new_quat = eq_quats[min_index]
        new_euler = quat_to_euler(new_quat)
        new_trajectory.append(new_euler)
    
    return new_trajectory
