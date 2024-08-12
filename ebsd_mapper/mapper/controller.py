"""
 Title:         Controller
 Description:   For conducting the mapping
 Author:        Janzen Choi

"""

# Libraries
import math
from copy import deepcopy
from ebsd_mapper.mapper.gridder import get_void_pixel_grid, read_pixels, VOID_PIXEL_ID
from ebsd_mapper.mapper.mapper import Mapper, NO_MAPPING
from ebsd_mapper.ebsd.map import Map
from ebsd_mapper.plotting.ebsd_plotter import EBSDPlotter
from ebsd_mapper.helper.general import transpose, round_sf
from ebsd_mapper.helper.io import dict_to_csv, csv_to_dict, get_file_path_exists
from ebsd_mapper.helper.plotter import define_legend, save_plot
from ebsd_mapper.maths.orientation import deg_to_rad, process_trajectory
from ebsd_mapper.plotting.pole_figure import IPF, get_lattice
from ebsd_mapper.plotting.grain_plotter import plot_grain

class Controller:

    def __init__(self):
        """
        Initialises the constructor class
        """
        self.headers = []
        self.min_area = None
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

    def import_ebsd(self, ebsd_path:str, step_size:float) -> None:
        """
        Reads in an EBSD map

        Parameters:
        * `ebsd_path`: Path to the EBSD file as a CSV file
        * `step_size`: Step size between coordinates
        """
        new_pixel_grid, new_grain_map = read_pixels(ebsd_path, step_size, self.headers)
        ebsd_map = Map(new_pixel_grid, new_grain_map, step_size)
        self.ebsd_maps.append(ebsd_map)

    def get_bounds(self) -> dict:
        """
        Returns the bounds of the imported EBSD map
        """

        # Gets the most recently added EBSD map
        pixel_grid = self.ebsd_maps[-1].get_pixel_grid()
        step_size  = self.ebsd_maps[-1].get_step_size()

        # Initialise bounds
        big_number = 1e7
        x_min, x_max, y_min, y_max = big_number, -big_number, big_number, -big_number

        # Iterate through elements and update bounds
        for row in range(len(pixel_grid)):
            for col in range(len(pixel_grid[row])):
                if pixel_grid[row][col] == VOID_PIXEL_ID:
                    continue
                x_min = min(col*step_size, x_min)
                x_max = max(col*step_size, x_max)
                y_min = min(row*step_size, y_min)
                y_max = max(row*step_size, y_max)

        # Return as a dictionary
        return {"x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max}

    def rebound_ebsd(self, x_min:float, x_max:float, y_min:float, y_max:float) -> None:
        """
        Redefines the lower and upper bounds of the most recently
        imported EBSD map
        
        Parameters:
        * `x_min`: The lowest x value for the new domain
        * `x_max`: The highest x value for the new domain
        * `y_min`: The lowest y value for the new domain
        * `y_max`: The highest y value for the new domain
        """

        # Gets the most recently added EBSD map
        pixel_grid = self.ebsd_maps[-1].get_pixel_grid()
        grain_map  = self.ebsd_maps[-1].get_grain_map()
        step_size  = self.ebsd_maps[-1].get_step_size()
        
        # Get boundaries
        x_min = round(x_min / step_size)
        x_max = round(x_max / step_size)
        y_min = round(y_min / step_size)
        y_max = round(y_max / step_size)

        # Get new and original lengths
        x_size = len(pixel_grid[0])
        y_size = len(pixel_grid)
        new_x_size = x_max - x_min
        new_y_size = y_max - y_min

        # Create new pixel grid and replace
        new_pixel_grid = get_void_pixel_grid(new_x_size, new_y_size)
        for row in range(y_size):
            for col in range(x_size):
                new_col, new_row = abs(col-x_min), abs(row-y_min)
                if new_col >= 0 and new_row >= 0 and new_col < new_x_size and new_row < new_y_size:
                    new_pixel_grid[new_row][new_col] = deepcopy(pixel_grid[row][col])
        self.ebsd_maps[-1].set_pixel_grid(new_pixel_grid)

        # Create new grain map and replace
        all_pixel_ids = list(set([pixel for pixel_list in new_pixel_grid for pixel in pixel_list]))
        new_grain_map = {}
        for pixel in all_pixel_ids:
            if pixel in grain_map.keys():
                new_grain_map[pixel] = grain_map[pixel]
        self.ebsd_maps[-1].set_grain_map(new_grain_map)

    def map_ebsd(self, radius:float, min_area:float, tolerance:float) -> None:
        """
        Maps the grains of the EBSD maps that have been read in
        
        Parameters:
        * `radius`:    The radius to do the mapping; (1.0 covers the whole map)
        * `min_area`:  The minimum area of the grains
        * `tolerance`: The maximum error to allow for a mapping
        """
        mapper = Mapper(self.ebsd_maps, radius, min_area, tolerance)
        self.map_dict = mapper.link_ebsd_maps()
        error_dict = mapper.get_error_dict()
        return error_dict

    def import_map(self, map_path:str) -> None:
        """
        Reads the grain mapping dictionary outputted by the script;
        saves time on remapping the EBSD maps

        Parameters:
        * `map_path`: The path to the mapping dictionary
        """
        self.map_dict = csv_to_dict(map_path)
        for key in self.map_dict.keys():
            self.map_dict[key] = [int(i) for i in self.map_dict[key]]

    def export_stats(self, stats_path:str, sort_stat:str, stats:list, add_header:bool, descending:bool) -> None:
        """
        Exports the statistics of the EBSD maps;
        only includes mappable grains if mapping has been done;
        available statistics include: ["grain_id", "area", "centroid_x", "centroid_y", "phi_1", "Phi", "phi_2"]

        Parameters:
        * `stats_path`: Path to save the dictionary (without extension)
        * `sort_stat`:  The statistic to order the statistics
        * `stats`:      The statistics to include in the exported file;
                        if undefined, exports all available statistics
        * `add_header`: Whether to include the header in the exported file
        * `descending`: Whether to sort the statistics in descending order
        """

        # Initialise
        available_stats = ["grain_id", "area", "centroid_x", "centroid_y", "phi_1", "Phi", "phi_2"]
        sort_stat_index = available_stats.index(sort_stat)
        data_dict_list = self.__get_stats__()

        # Iterate through EBSD maps
        for i, data_dict in enumerate(data_dict_list):

            # Sort data
            data_list = list(data_dict.values())
            combined_lists = zip(*data_list)
            sorted_lists = sorted(combined_lists, key=lambda pair: pair[sort_stat_index], reverse=descending)

            # Create the dictionary of statistics
            stats_dict = {}
            for stat in stats:
                stat_index = available_stats.index(stat)
                stats_dict[stat] = [sl[stat_index] for sl in sorted_lists]

            # Save dictionary
            curr_stats_path = stats_path if len(data_dict_list) == 1 else f"{stats_path}_{i+1}"
            curr_stats_path = get_file_path_exists(curr_stats_path, "csv")
            dict_to_csv(stats_dict, curr_stats_path, add_header=add_header)

    def export_map(self, map_path:str) -> None:
        """
        Converts the grain mapping dictionary into a CSV file

        Parameters:
        * `map_path`: Path to save the dictionary
        """
        map_path = get_file_path_exists(map_path, "csv")
        dict_to_csv(self.map_dict, map_path)

    def export_reorientation(self, reorientation_path:str, process:bool) -> None:
        """
        Calculates and saves the reorientation trajectories of the mapped grains

        Parameters:
        * `reorientation_path`: Path to save the dictionary
        * `process`:            Whether to process the reorientation trajectories
        """
        
        # Get reorientation data
        reorientation_dict = self.__get_reorientation__()
        if process:
            for grain_id in reorientation_dict.keys():
                reorientation_dict[grain_id] = process_trajectory(reorientation_dict[grain_id])
        
        # Reformat reorientation data
        new_reorientation_dict = {}
        for grain_id in reorientation_dict.keys():
            data = transpose(reorientation_dict[grain_id])
            new_reorientation_dict[f"g{grain_id}_phi_1"] = data[0]
            new_reorientation_dict[f"g{grain_id}_Phi"]   = data[1]
            new_reorientation_dict[f"g{grain_id}_phi_2"] = data[2]
        
        # Write reorientation data to CSV file
        reorientation_path = get_file_path_exists(reorientation_path, "csv")
        dict_to_csv(new_reorientation_dict, reorientation_path)

    def plot_ebsd(self, ebsd_path:str, ipf:str="x", figure_x:float=10,
                  grain_id:bool=False, boundary:bool=False, id_list:list=None) -> None:
        """
        Plots the EBSD maps

        Parameters:
        * `ebsd_path`: The path to save the EBSD files
        * `ipf`:       The IPF colour ("x", "y", "z")
        * `figure_x`:  The initial horizontal size of the figures
        * `grain_id`:  Whether to include IDs in the EBSD maps;
                       define dictionary for custom settings
        * `boundary`:  Whether to include IDs in the EBSD maps;
                       define dictionary for custom settings
        * `id_list`:   The IDs of the grains to plot the IDs and boundaries;
                       if undefined, adds for all grains
        """

        # Define settings
        id_settings = grain_id if isinstance(grain_id, dict) else {"fontsize": 20, "color": "black"}
        boundary_settings = boundary if isinstance(boundary, dict) else {"linewidth": 1, "color": "black"}
        
        # Get grain IDs for each map
        if len(self.map_dict.keys()) > 0:
            id_grid = []
            mappings = list(self.map_dict.keys())
            for i in range(len(self.map_dict[mappings[0]])):
                grain_list = [self.map_dict[mapping][i] for mapping in mappings]
                if id_list == None or grain_list[0] in id_list:
                    id_grid.append(grain_list)
            id_grid = transpose(id_grid)
        
        # Initialise figure dimensions
        current_figure_x = figure_x
        initial_x_size = len(self.ebsd_maps[0].get_pixel_grid()[0])*self.ebsd_maps[0].get_step_size()

        # Iterate through EBSD maps
        for i, ebsd_map in enumerate(self.ebsd_maps):
            
            # Plot EBSD maps
            current_x_size = len(ebsd_map.get_pixel_grid()[0])*ebsd_map.get_step_size()
            current_figure_x = figure_x*current_x_size/initial_x_size
            plotter = EBSDPlotter(ebsd_map, current_figure_x)
            plotter.plot_ebsd(ipf)

            # Add IDs and boundaries if specified, and save
            include = id_list if len(self.map_dict.keys()) == 0 else id_grid[i]
            if (isinstance(grain_id, bool) and grain_id) or isinstance(grain_id, dict):
                plotter.plot_ids(include, settings=id_settings)
            if (isinstance(boundary, bool) and boundary) or isinstance(boundary, dict):
                plotter.plot_boundaries(include, settings=boundary_settings)
            curr_ebsd_path = ebsd_path if len(self.ebsd_maps) == 1 else f"{ebsd_path}_{i+1}"
            save_plot(f"{curr_ebsd_path}.png")

    def plot_grain(self, grain_id:int, plot_path:str, ipf:str="x") -> None:
        """
        Plots changes to a single grain

        Parameter:
        * `grain_id`: The grain ID
        * `plot_path: Path to the plot
        * `ipf`:      The IPF direction
        """
        plot_grain(
            plot_path       = f"{plot_path}.png",
            pixel_grid_list = [ebsd_map.get_pixel_grid() for ebsd_map in self.ebsd_maps],
            grain_map_list  = [ebsd_map.get_grain_map() for ebsd_map in self.ebsd_maps],
            step_size_list  = [ebsd_map.get_step_size() for ebsd_map in self.ebsd_maps],
            map_dict        = self.map_dict,
            grain_id        = grain_id,
            ipf             = ipf
        )

    def plot_reorientation(self, plot_path:str, structure:str="fcc", direction:list=[1,0,0], grain_ids:list=None) -> None:
        """
        Plots the reorientation trajectories on an inverse pole figure

        Parameters:
        * `plot_path`: Path to save the plot
        * `structure`: Crystal structure ("bcc", "fcc")
        * `direction`: Direction to plot the IPF
        * `grain_ids`: List of grain IDs to plot; if undefined, plots all mappable grains
        """

        # Initialise plotter
        lattice = get_lattice(structure)
        ipf = IPF(lattice)

        # Plot raw reorientation trajectories
        reorientation_dict = self.__get_reorientation__(grain_ids)
        raw_trajectories = [reorientation_dict[grain_id] for grain_id in grain_ids]
        ipf.plot_ipf_trajectory(raw_trajectories, direction, "plot", {"color": "darkgray", "linewidth": 2})
        ipf.plot_ipf_trajectory(raw_trajectories, direction, "arrow", {"color": "darkgray", "head_width": 0.01, "head_length": 0.015})
        for grain_id, et in zip(grain_ids, raw_trajectories):
            ipf.plot_ipf_trajectory([[et[0]]], direction, "scatter", {"color": "darkgray", "s": 8**2})
            ipf.plot_ipf_trajectory([[et[0]]], direction, "text", {"color": "black", "fontsize": 8, "s": grain_id})

        # Plot processed reorientation trajectories
        sim_trajectories = [process_trajectory(raw_trajectory) for raw_trajectory in raw_trajectories]
        ipf.plot_ipf_trajectory(sim_trajectories, direction, "plot", {"color": "green", "linewidth": 1, "zorder": 3})
        ipf.plot_ipf_trajectory(sim_trajectories, direction, "arrow", {"color": "green", "head_width": 0.005, "head_length": 0.005*1.5, "zorder": 3})
        ipf.plot_ipf_trajectory([[st[0]] for st in sim_trajectories], direction, "scatter", {"color": "green", "s": 4**2, "zorder": 3})  
        
        # Format and save plot
        define_legend(["darkgray", "green"], ["Raw", "Processed"], ["line", "line"])
        plot_path = get_file_path_exists(plot_path, "png")
        save_plot(plot_path)

    def __get_reorientation__(self, grain_ids:list=None) -> dict:
        """
        Calculates the reorientation trajectories of the mapped grains
        
        Parameters:
        * `grain_ids`: The list of grain IDs to calculate the trajectories of;
                       Uses all the grain IDs if undefined
                       
        Returns a dictionary of the reorientation trajectories (rads)
        """

        # Define grain IDs and initialise dictionary
        if grain_ids != None:
            grain_ids = [grain_id for grain_id in grain_ids if grain_id in self.map_dict["ebsd_1"]]
        else:
            grain_ids = self.map_dict["ebsd_1"]
        reorientation_dict = dict(zip(grain_ids, [[] for _ in range(len(grain_ids))]))

        # Get reorientation trajectories
        for grain_id in grain_ids:
            base_index = self.map_dict["ebsd_1"].index(grain_id)
            for j, ebsd_map in enumerate(self.ebsd_maps):
                mapped_id = self.map_dict[f"ebsd_{j+1}"][base_index]
                if mapped_id == NO_MAPPING and j == 0:
                    reorientation_dict[grain_id].append([0.0,0.0,0.0])
                elif mapped_id == NO_MAPPING and j > 0:
                    reorientation_dict[grain_id].append(reorientation_dict[grain_id][-1])
                else:
                    orientation = ebsd_map.get_grain(mapped_id).get_orientation()
                    orientation = deg_to_rad(list(orientation))
                    reorientation_dict[grain_id].append(orientation)

        # Returns the dictionary
        return reorientation_dict

    def __get_stats__(self) -> list:
        """
        Gets statistics from the EBSD maps;
        returns lists of dictionaries of the grain ids, area list,
        centroid_x list, centroid_y list, phi_1 list, Phi list, and phi_2 list
        """

        # Iterate through EBSD maps
        data_dict_list = []
        for i, ebsd_map in enumerate(self.ebsd_maps):

            # Get grain IDs
            if f"ebsd_{i+1}" in self.map_dict.keys():
                grain_ids = self.map_dict[f"ebsd_{i+1}"]
            else:
                grain_ids = ebsd_map.get_grain_ids()

            # Calculate areas
            step_size = ebsd_map.get_step_size()
            step_area = math.pow(step_size, 2)
            area_list = [ebsd_map.get_grain(grain_id).get_size()*step_area for grain_id in grain_ids]
            
            # Calculate centroids
            centroid_dict = ebsd_map.get_centroids()
            centroid_x_list = [centroid_dict[grain_id][0]*step_size for grain_id in grain_ids]
            centroid_y_list = [centroid_dict[grain_id][1]*step_size for grain_id in grain_ids]

            # Get orientations
            orientation_list = [ebsd_map.get_grain(grain_id).get_orientation() for grain_id in grain_ids]
            phi_1_list = [deg_to_rad(o[0]) for o in orientation_list]
            Phi_list   = [deg_to_rad(o[1]) for o in orientation_list]
            phi_2_list = [deg_to_rad(o[2]) for o in orientation_list]

            # Round orientations
            phi_1_list = [round_sf(phi, 5) for phi in phi_1_list]
            Phi_list   = [round_sf(phi, 5) for phi in Phi_list]
            phi_2_list = [round_sf(phi, 5) for phi in phi_2_list]

            # Store the extracted data
            data_dict_list.append({
                "grain_ids":  grain_ids,
                "area":       area_list,
                "centroid_x": centroid_x_list,
                "centroid_y": centroid_y_list,
                "phi_1":      phi_1_list,
                "Phi":        Phi_list,
                "phi_2":      phi_2_list,
            })

        # Returns the data
        return data_dict_list
