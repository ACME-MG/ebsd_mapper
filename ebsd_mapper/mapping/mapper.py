"""
 Title:         Mapper
 Description:   Maps the grains in multiple EBSD maps
 Author:        Janzen Choi

"""

# Libraries
import math
from ebsd_mapper.mapping.edge import Edge
from ebsd_mapper.mapping.gridder import get_centroids, get_max_grain_id, shift_pixel_grid, shift_grain_map
from ebsd_mapper.maths.csl import get_disorientation
from ebsd_mapper.maths.orientation import deg_to_rad

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

def map_ebsd(pixel_grid_1:list, pixel_grid_2:list, grain_map_1:dict, grain_map_2:dict,
             id_list_1:list=None, id_list_2:list=None) -> dict:
    """
    Maps grains from multiple EBSD maps
    
    Parameters:
    * `pixel_grid_1`: First grid of pixels
    * `pixel_grid_2`: Second grid of pixels
    * `grain_map_1`:  First mapping of grains
    * `grain_map_2`:  Second mapping of grains
    * `id_list_1`:    First list of grain IDs to do the mapping
    * `id_list_2`:    Second list of grain IDs to do the mapping
    
    Returns the mapping of the grains as a dictionary
    """

    # Make all grain IDs unique
    max_id_1 = get_max_grain_id(pixel_grid_1)
    pixel_grid_2 = shift_pixel_grid(pixel_grid_2, max_id_1)
    grain_map_2 = shift_grain_map(grain_map_2, max_id_1)

    # Identify grains to do mapping
    grain_ids_1 = list(grain_map_1.keys())
    if id_list_1 != None:
        grain_ids_1 = [grain_id for grain_id in grain_ids_1 if grain_id in id_list_1]
    grain_ids_2 = list(grain_map_2.keys())
    if id_list_2 != None:
        grain_ids_2 = [grain_id for grain_id in grain_ids_2 if grain_id-max_id_1 in id_list_2]

    # Initialise edge list
    edge_list = []
    for grain_id_1 in grain_ids_1:
        for grain_id_2 in grain_ids_2:
            edge = Edge(grain_id_1, grain_id_2)
            edge_list.append(edge)
    if edge_list == []:
        return None

    # Initialise discrepancy sources
    centroid_dict_1 = get_norm_centroids(pixel_grid_1)
    centroid_dict_2 = get_norm_centroids(pixel_grid_2)
    area_dict_1 = get_norm_areas(pixel_grid_1)
    area_dict_2 = get_norm_areas(pixel_grid_2)
    
    # Calculate errors
    error_dict = {"centroid_error": [], "orientation_error": [], "area_error": []}
    for edge in edge_list:
        grain_id_1 = edge.get_node_1()
        grain_id_2 = edge.get_node_2()

        # Calculate centroid error
        x_1, y_1 = centroid_dict_1[grain_id_1]
        x_2, y_2 = centroid_dict_2[grain_id_2]
        centroid_error = math.sqrt(math.pow(x_1-x_2,2) + math.pow(y_1-y_2,2))
        error_dict["centroid_error"].append(centroid_error)

        # Calculate orientation error
        euler_1 = grain_map_1[grain_id_1].get_orientation()
        euler_1 = deg_to_rad(list(euler_1))
        euler_2 = grain_map_2[grain_id_2].get_orientation()
        euler_2 = deg_to_rad(list(euler_2))
        disorientation = get_disorientation(euler_1, euler_2, "cubic")
        orientation_error = disorientation
        error_dict["orientation_error"].append(orientation_error)

        # Calculate area error
        area_1 = area_dict_1[grain_id_1]
        area_2 = area_dict_2[grain_id_2]
        area_error = abs(area_1 - area_2)/area_1
        error_dict["area_error"].append(area_error)

    # Normalise errors and define weights of edges
    for name in ["centroid_error", "orientation_error", "area_error"]:
        error_dict[name] = linear_map_list(error_dict[name])
        for i, edge in enumerate(edge_list):
            edge.add_error(error_dict[name][i])

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
