"""
 Title:         Changer
 Description:   Simulates changes to the microstructure
 Author:        Janzen Choi

"""

# Libraries
import random
from copy import deepcopy
from ebsd_mapper.mapping.gridder import get_void_pixel_grid, remap_grains, VOID_PIXEL_ID
from ebsd_mapper.mapping.neighbour import get_neighbour_dict
from ebsd_mapper.helper.general import round_sf

def deform_x(pixel_grid:list, step_size:float, factor:float) -> list:
    """
    Deforms a grid of pixels in the x direction

    Parameters:
    * `pixel_grid`: A grid of pixels
    * `step_size`:  The size of each pixel
    * `factor`:     The factor to deform

    Returns the deformed grid of pixels
    """

    # Initialise new pixel grid
    x_len = len(pixel_grid[0])
    y_len = len(pixel_grid)
    new_x_len = round(factor*x_len*step_size/step_size)
    new_pixel_grid = get_void_pixel_grid(new_x_len, y_len)

    # Populate new pixel grid
    for row in range(len(new_pixel_grid)):
        for col in range(len(new_pixel_grid[0])):
            original_col = round(col*step_size/step_size/factor)
            try:
                new_pixel_grid[row][col] = pixel_grid[row][original_col]
            except:
                pass

    # Remove voids and return new grid
    new_pixel_grid = remove_column_void(new_pixel_grid)
    return new_pixel_grid

def deform_y(pixel_grid:list, step_size:float, factor:float) -> list:
    """
    Deforms a grid of pixels in the y direction

    Parameters:
    * `pixel_grid`: A grid of pixels
    * `step_size`:  The size of each pixel
    * `factor`:     The factor to deform

    Returns the deformed grid of pixels
    """
    new_pixel_grid = list(zip(*pixel_grid[::-1]))
    new_pixel_grid = deform_x(new_pixel_grid, step_size, factor)
    for _ in range(3):
        new_pixel_grid = list(zip(*new_pixel_grid[::-1]))
    for row in range(len(new_pixel_grid)):
        new_pixel_grid[row] = list(new_pixel_grid[row])
    return new_pixel_grid

def remove_column_void(pixel_grid:list) -> list:
    """
    Removes the void pixels at specific columns

    Parameters:
    * `pixel_grid`: A grid of pixels

    Returns the new pixel grid
    """
    removed = False
    for col in range(len(pixel_grid[0])):
        if pixel_grid[0][col] == VOID_PIXEL_ID:
            pixel_grid = deepcopy(pixel_grid)
            for row in range(len(pixel_grid)):
                pixel_grid[row].pop(col)
            removed = True
            break
    if removed:
        pixel_grid = remove_column_void(pixel_grid)
    return pixel_grid

def orient_noise(grain_map:dict, max_noise:float=5.0) -> dict:
    """
    Adds noise to the orientations of the grains

    Parameters:
    * `grain_map`: A dictionary of grains
    * `max_noise`: Maximum noise value

    Returns reoriented grain dictionary
    """
    new_grain_map = deepcopy(grain_map)
    for grain_id in grain_map.keys():
        orientation = grain_map[grain_id].get_orientation()
        new_orientation = []
        for phi in orientation:
            new_phi = round_sf(phi + random.uniform(-max_noise, max_noise), 5)
            new_orientation.append(new_phi)
        new_grain_map[grain_id].set_orientation(*new_orientation)
    return new_grain_map

def merge_grains(pixel_grid:list, grain_map:dict, probability:float=0.1) -> tuple:
    """
    Merges grains

    Parameters:
    * `pixel_grid`:  A grid of pixels
    * `grain_map`:   A dictionary of grains
    * `probability`: Probability of combining

    Returns the new pixel grid and grain map
    """

    # Determine which grains to merge
    neighbour_dict = get_neighbour_dict(pixel_grid)
    merge_dict = {}
    for grain_id in neighbour_dict.keys():
        for n_id in neighbour_dict[grain_id]:
            if random.random() < probability:
                merge_dict[n_id] = grain_id

    # Start merging grains
    pixel_grid = deepcopy(pixel_grid)
    for row in range(len(pixel_grid)):
        for col in range(len(pixel_grid[0])):
            grain_id = pixel_grid[row][col]
            if grain_id in merge_dict.keys():
                pixel_grid[row][col] = merge_dict[grain_id]

    # Remap and return new pixel grid
    pixel_grid, grain_map = remap_grains(pixel_grid, grain_map)
    return pixel_grid, grain_map
