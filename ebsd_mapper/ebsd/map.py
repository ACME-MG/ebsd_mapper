"""
 Title:         Map
 Description:   Stores information about an EBSD map
 Author:        Janzen Choi

"""

# Libraries
import math, numpy as np
from ebsd_mapper.ebsd.grain import Grain
from ebsd_mapper.helper.general import flatten
from ebsd_mapper.mapper.gridder import VOID_PIXEL_ID

# The Map class
class Map:
    
    def __init__(self, pixel_grid:list, grain_map:dict, step_size:float):
        """
        Constructor for the Map class
        
        Parameters:
        * `pixel_grid`: Grid of grain IDs
        * `grain_map`:  Dictionary mapping grain IDs to grain objects
        * `step_size`:  Step size of grid
        """
        self.pixel_grid = pixel_grid
        self.grain_map  = grain_map
        self.step_size  = step_size
        
    def get_pixel_grid(self) -> list:
        """
        Returns the pixel grid
        """
        return self.pixel_grid
        
    def get_grain_map(self) -> dict:
        """
        Returns the grain map
        """
        return self.grain_map
        
    def get_step_size(self) -> float:
        """
        Returns the step size
        """
        return self.step_size

    def set_pixel_grid(self, pixel_grid:list) -> None:
        """
        Sets the pixel grid
        
        Parameters:
        * `pixel_grid`: Grid of grain IDs
        """
        self.pixel_grid = pixel_grid
        
    def set_grain_map(self, grain_map:dict) -> None:
        """
        Sets the grain map
        
        Parameters:
        * `grain_map`: Dictionary mapping grain IDs to grain objects
        """
        self.grain_map = grain_map
        
    def set_step_size(self, step_size:float) -> None:
        """
        Sets the step size
        
        Parameters:
        * `step_size`: Step size of grid
        """
        self.step_size = step_size

    def get_grain_ids(self, min_area:float=None) -> list:
        """
        Gets the list of grain IDs
        
        Parameters:
        * `min_area`: The minimum area to include the grains
        
        Returns the list of grain IDs
        """
        
        # Get raw grain IDs from pixel grid
        grain_ids = list(set(flatten(self.pixel_grid)))
        if VOID_PIXEL_ID in grain_ids:
            grain_ids.remove(VOID_PIXEL_ID)
        
        # Remove grains under minimum area if specified
        if min_area != None:
            min_area_scaled = min_area / math.pow(self.step_size, 2)
            grain_ids = [grain_id for grain_id in grain_ids if self.grain_map[grain_id].get_size() >= min_area_scaled]
        
        # Sort grain IDs and return
        grain_ids = sorted(grain_ids)
        return grain_ids

    def get_grain(self, grain_id:int) -> Grain:
        """
        Gets the grain object given an ID
        
        Parameters:
        * `grain_id`: The ID of the grain
        
        Returns the grain object
        """
        return self.grain_map[grain_id]

    def get_centroids(self) -> dict:
        """
        Gets the centroids for all the grains
        """
        
        # Initialise dictionary to store pixel positions
        grain_ids = self.get_grain_ids()
        pixel_dict = {}
        for grain_id in grain_ids:
            pixel_dict[grain_id] = {"x": [], "y": []}
        
        # Add points to the pixel dictionary
        for row in range(len(self.pixel_grid)):
            for col in range(len(self.pixel_grid[row])):
                grain_id = self.pixel_grid[row][col]
                if grain_id == VOID_PIXEL_ID:
                    continue
                pixel_dict[self.pixel_grid[row][col]]["x"].append(col)
                pixel_dict[self.pixel_grid[row][col]]["y"].append(row)
        
        # Calculate centroids
        centroid_dict = {}
        for grain_id in grain_ids:
            x_mean = np.average(pixel_dict[grain_id]["x"])
            y_mean = np.average(pixel_dict[grain_id]["y"])
            centroid_dict[grain_id] = (x_mean, y_mean)
        return centroid_dict

    def get_norm_centroids(self) -> dict:
        """
        Gets normalised centroids of a grid relative
        to the centre of the grid
        """
        x_size = len(self.pixel_grid[0])
        y_size = len(self.pixel_grid)
        centroid_dict = self.get_centroids()
        for grain_id in centroid_dict.keys():
            x, y = centroid_dict[grain_id]
            centroid_dict[grain_id] = ((x-x_size/2)/x_size, (y-y_size/2)/y_size)
        return centroid_dict

    def get_norm_areas(self) -> dict:
        """
        Gets normalised areas of a grid
        """

        # Get dimensions of pixel grid
        x_len = len(self.pixel_grid[0])
        y_len = len(self.pixel_grid)
        total_area = x_len*y_len

        # Initialise area dictionary
        area_dict = {}
        grain_ids = self.get_grain_ids()
        for grain_id in grain_ids:
            area_dict[grain_id] = 0

        # Get areas
        for row in range(y_len):
            for col in range(x_len):
                area_dict[self.pixel_grid[row][col]] += 1
        
        # Normalise and return
        for grain_id in grain_ids:
            area_dict[grain_id] /= total_area
        return area_dict
        