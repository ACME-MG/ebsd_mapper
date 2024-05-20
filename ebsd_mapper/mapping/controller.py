"""
 Title:         Controller
 Description:   For conducting the mapping
 Author:        Janzen Choi

"""

# Libraries
from ebsd_mapper.mapping.gridder import read_pixels
from ebsd_mapper.mapping.mapper import map_ebsd
from ebsd_mapper.mapping.plotter import Plotter, save_plot
from ebsd_mapper.helper.general import transpose
from ebsd_mapper.helper.io import dict_to_csv, get_file_path_writable

# Constants
NO_MAPPING = ""

class Controller:

    def __init__(self):
        """
        Initialises the constructor class
        """
        self.headers = []
        self.ebsd_maps = []
        self.map_dict = {}

    def define_headers(self, x:str, y:str, grain_id:str, phi_1:str, Phi:str, phi_2:str) -> None:
        """
        Defines the necessary headers for the CSV files

        Parameters:
        * `x`:        Header for the x-coordinate
        * `y`:        Header for the y-coordinate
        * `grain_id`: Header for the grain ID
        * `phi_1`:    Header for the phi_1 values
        * `Phi`:      Header for the Phi values
        * `phi_2`:    Header for the phi_2 values
        """
        self.headers = [x, y, grain_id, phi_1, Phi, phi_2]

    def add_ebsd(self, ebsd_path:str, step_size:float) -> None:
        """
        Adds an EBSD map

        Parameters:
        * `ebsd_path`: Path to the EBSD file as a CSV file
        * `step_size`: Step size between coordinates
        """

        # Extract grain information; if first map, add all grain IDs
        new_pixel_grid, new_grain_map = read_pixels(ebsd_path, step_size, self.headers)
        if len(self.ebsd_maps) == 0:
            self.map_dict[f"ebsd_1"] = sorted(list(new_grain_map.keys()))
        
        # Otherwise, try to do grain mapping with new grain information
        else:

            # Get last EBSD map
            old_pixel_grid = self.ebsd_maps[-1]["pixel_grid"]
            old_grain_map = self.ebsd_maps[-1]["grain_map"]
            old_grain_ids = self.map_dict[f"ebsd_{len(self.ebsd_maps)}"]

            # Get new grain IDs
            map_dict = map_ebsd(old_pixel_grid, old_grain_map, new_pixel_grid, new_grain_map)
            new_grain_ids = []
            for grain_id in old_grain_ids:
                if grain_id in map_dict.keys():
                    new_grain_ids.append(map_dict[grain_id])
                else:
                    new_grain_ids.append(NO_MAPPING)
            self.map_dict[f"ebsd_{len(self.ebsd_maps)+1}"] = new_grain_ids

        # Add new grain information
        ebsd_map = {"pixel_grid": new_pixel_grid, "grain_map": new_grain_map, "step_size": step_size}
        self.ebsd_maps.append(ebsd_map)

    def plot_ebsd(self, ebsd_path:str, ipf:str="x", figure_x:float=10,
                  include_id:bool=False,include_boundary:bool=False, id_list:list=None) -> None:
        """
        Plots the EBSD maps

        Parameters:
        * `ebsd_path`:        The path to save the EBSD files
        * `ipf`:              The IPF colour ("x", "y", "z")
        * `figure_x`:         The horizontal size of the figures
        * `include_id`:       Whether to include IDs in the EBSD maps;
                              define dictionary for custom settings
        * `include_boundary`: Whether to include IDs in the EBSD maps;
                              define dictionary for custom settings
        * `id_list`:          The IDs of the grains to add the IDs and boundaries;
                              if undefined, adds for all grains
        """

        # Define settings
        id_settings = include_id if isinstance(include_id, dict) else {"fontsize": 20, "color": "black"}
        boundary_settings = include_boundary if isinstance(include_boundary, dict) else {"linewidth": 1, "color": "black"}
        
        # Get grain IDs for each map
        id_grid = []
        mappings = list(self.map_dict.keys())
        for i in range(len(self.map_dict[mappings[0]])):
            grain_list = [self.map_dict[mapping][i] for mapping in mappings]
            if not NO_MAPPING in grain_list and (id_list == None or grain_list[0] in id_list):
                id_grid.append(grain_list)
        id_grid = transpose(id_grid)
        
        # Iterate through EBSD maps
        for i, ebsd_map in enumerate(self.ebsd_maps):
            
            # Plot EBSD maps
            plotter = Plotter(ebsd_map["pixel_grid"], ebsd_map["grain_map"], ebsd_map["step_size"], figure_x)
            plotter.plot_ebsd(ipf)
            if isinstance(include_id, bool) and include_id:
                plotter.plot_ids(id_grid[i], settings=id_settings)
            if isinstance(include_boundary, bool) and include_boundary:
                plotter.plot_boundaries(id_grid[i], settings=boundary_settings)
            save_plot(f"{ebsd_path}_{i+1}.png")

    def export_map(self, map_path:str) -> None:
        """
        Exports the grain mapping dictionary

        Parameters:
        * `map_path`: Path to save the dictionary
        """
        map_path = get_file_path_writable(map_path, "csv")
        dict_to_csv(self.map_dict, map_path)
