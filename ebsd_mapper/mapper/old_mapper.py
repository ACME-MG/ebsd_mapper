"""
 Title:         Mapper
 Description:   Maps the grains in multiple EBSD maps
 Author:        Janzen Choi

"""

# Libraries
import math
from ebsd_mapper.mapper.edge import Edge
from ebsd_mapper.helper.general import transpose
from ebsd_mapper.mapper.gridder import get_centroids, get_max_grain_id, shift_pixel_grid, shift_grain_map
from ebsd_mapper.maths.orientation import get_geodesic, deg_to_rad

def get_norm_centroids(pixel_grid:list) -> dict:
    """
    Gets normalised centroids of a grid relative
    to the centre of the grid
    
    Parameters:
    * `pixel_grid`: First grid of pixels

    Returns the normalised centroid map
    """
    x_size = len(pixel_grid[0])
    y_size = len(pixel_grid)
    centroid_dict = get_centroids(pixel_grid)
    for grain_id in centroid_dict.keys():
        x, y = centroid_dict[grain_id]
        centroid_dict[grain_id] = ((x-x_size/2)/x_size, (y-y_size/2)/y_size)
    return centroid_dict

def get_norm_areas(pixel_grid:list) -> dict:
    """
    Gets normalised areas of a grid
    
    Parameters:
    * `pixel_grid`: First grid of pixels

    Returns the normalised area map
    """

    # Get dimensions of pixel grid
    x_len = len(pixel_grid[0])
    y_len = len(pixel_grid)
    total_area = x_len*y_len

    # Initialise area dictionary
    area_dict = {}
    grain_ids = list(set([pixel for pixel_list in pixel_grid for pixel in pixel_list]))
    for grain_id in grain_ids:
        area_dict[grain_id] = 0

    # Get areas
    for row in range(y_len):
        for col in range(x_len):
            area_dict[pixel_grid[row][col]] += 1
    
    # Normalise and return
    for grain_id in grain_ids:
        area_dict[grain_id] /= total_area
    return area_dict

def linear_map(value:float, in_l:float, in_u:float, out_l:float, out_u:float) -> float:
    """
    Linearly maps a value

    Parameters:
    * `value`:  The value to be mapped
    * `in_l`:   The lower bound of the input
    * `in_u`:   The upper bound of the input
    * `out_l`:  The lower bound of the output
    * `out_u`:  The upper bound of the output

    Returns the mapped value
    """
    if in_l == in_u or out_l == out_u:
        return value
    factor = (out_u - out_l) / (in_u - in_l)
    return (value - in_l) * factor + out_l

def linear_map_list(value_list:list) -> list:
    """
    Linearly maps a list of values

    Parameters:
    * `value_list`: A list of values
    
    Returns the mapped list of values
    """
    in_l = min(value_list)
    in_u = max(value_list)
    mapped_list = [linear_map(value, in_l, in_u, 0, 1) for value in value_list]
    return mapped_list

def map_ebsd(pixel_grid_1:list, pixel_grid_2:list, grain_map_1:dict,
             grain_map_2:dict, id_list_1:list, id_list_2:list, radius:float=0.3) -> dict:
    """
    Maps grains from multiple EBSD maps
    
    Parameters:
    * `pixel_grid_1`: First grid of pixels
    * `pixel_grid_2`: Second grid of pixels
    * `grain_map_1`:  First mapping of grains
    * `grain_map_2`:  Second mapping of grains
    * `id_list_1`:    First list of grain IDs to do the mapping
    * `id_list_2`:    Second list of grain IDs to do the mapping
    * `radius`:       The radius to do the mapping; (1.0 covers the whole map)
    
    Returns the mapping of the grains as a dictionary
    """

    # Make all grain IDs unique
    max_id_1 = get_max_grain_id(pixel_grid_1)
    pixel_grid_2 = shift_pixel_grid(pixel_grid_2, max_id_1)
    grain_map_2 = shift_grain_map(grain_map_2, max_id_1)

    # Identify grains to do mapping
    grain_ids_1 = list(grain_map_1.keys())
    grain_ids_1 = [grain_id for grain_id in grain_ids_1 if grain_id in id_list_1]
    grain_ids_2 = list(grain_map_2.keys())
    grain_ids_2 = [grain_id for grain_id in grain_ids_2 if grain_id-max_id_1 in id_list_2]

    # Initialise discrepancy sources
    centroid_dict_1 = get_norm_centroids(pixel_grid_1)
    centroid_dict_2 = get_norm_centroids(pixel_grid_2)
    area_dict_1 = get_norm_areas(pixel_grid_1)
    area_dict_2 = get_norm_areas(pixel_grid_2)
    
    # Initialise edge list
    edge_list = []
    for grain_id_1 in grain_ids_1:
        
        # Get distances
        c_1 = centroid_dict_1[grain_id_1]
        get_dist = lambda c_2 : math.sqrt(math.pow(c_1[0]-c_2[0], 2) + math.pow(c_1[1]-c_2[1], 2))
        distance_list = [get_dist(centroid_dict_2[grain_id_2]) for grain_id_2 in grain_ids_2]

        # Initial properties of grains within close proximity
        close_ids_2 = []
        error_grid = [[] for _ in range(3)]
        
        # Calculate errors for grains within close proximity
        for grain_id_2, distance in zip(grain_ids_2, distance_list):
            
            # Consider connection if within close proximity
            if distance > radius:
                continue
            close_ids_2.append(grain_id_2)
            
            # Calculate geodesic distance
            euler_1 = deg_to_rad(list(grain_map_1[grain_id_1].get_orientation()))
            euler_2 = deg_to_rad(list(grain_map_2[grain_id_2].get_orientation()))
            geodesic = get_geodesic(euler_1, euler_2)
            
            # Calculate area error
            area_1 = area_dict_1[grain_id_1]
            area_2 = area_dict_2[grain_id_2]
            area_diff = abs((area_1-area_2)/area_1)
            
            # Add errors
            error_grid[0].append(distance)
            error_grid[1].append(geodesic)
            error_grid[2].append(area_diff)
    
        # Add weighted edge to edge list based on normalised error
        error_grid = transpose([linear_map_list(error_list) for error_list in error_grid])
        for close_id_2, error_list in zip(close_ids_2, error_grid):
            edge = Edge(grain_id_1, close_id_2)
            for error in error_list:
                edge.add_error(error)
            edge_list.append(edge)

    # Alert if no mappings
    if edge_list == []:
        return None
    
    # Initialise mapping information
    weight_list = [edge.get_weight() for edge in edge_list]
    sorted_weight_list = sorted(weight_list)

    # Find minimum edge combination between two disjoint sets of nodes
    node_list_1, node_list_2 = [], []
    for weight in sorted_weight_list:
        edge = edge_list[weight_list.index(weight)]
        if edge.get_node_1() in node_list_1 or edge.get_node_2() in node_list_2:
            continue
        node_list_1.append(edge.get_node_1())
        node_list_2.append(edge.get_node_2())

    # Return the mapping dictionary
    node_list_2 = [id - max_id_1 for id in node_list_2]
    map_dict = dict(zip(node_list_1, node_list_2))
    return map_dict
