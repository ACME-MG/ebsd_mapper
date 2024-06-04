"""
 Title:         Controller
 Description:   For conducting the mapping
 Author:        Janzen Choi

"""

# Libraries
import math
from ebsd_mapper.mapping.gridder import read_pixels, get_centroids
from ebsd_mapper.mapping.mapper import map_ebsd
from ebsd_mapper.plotting.ebsd_plotter import EBSDPlotter
from ebsd_mapper.helper.general import transpose, integer_to_ordinal
from ebsd_mapper.helper.io import dict_to_csv, csv_to_dict, get_file_path_exists
from ebsd_mapper.helper.plotter import save_plot
from ebsd_mapper.maths.orientation import deg_to_rad
from ebsd_mapper.plotting.pole_figure import IPF, get_lattice, get_trajectories
from ebsd_mapper.plotting.grain_plotter import plot_grain

# Constants
NO_MAPPING = ""

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

    def define_min_area(self, min_area:float) -> None:
        """
        Defines the minimum area to do the mapping for

        Parameters:
        *  `min_area`: The minimum area
        """
        self.min_area = min_area

    def import_ebsd(self, ebsd_path:str, step_size:float) -> None:
        """
        Reads in an EBSD map

        Parameters:
        * `ebsd_path`: Path to the EBSD file as a CSV file
        * `step_size`: Step size between coordinates
        """
        new_pixel_grid, new_grain_map = read_pixels(ebsd_path, step_size, self.headers)
        ebsd_map = {"pixel_grid": new_pixel_grid, "grain_map": new_grain_map, "step_size": step_size}
        self.ebsd_maps.append(ebsd_map)

    def map_ebsd(self) -> None:
        """
        Maps the grains of the EBSD maps that have been read in
        """

        # Get initial map
        first_grain_map = self.ebsd_maps[0]["grain_map"]
        first_step_size = self.ebsd_maps[0]["step_size"]
        new_grain_ids = get_grain_ids(first_grain_map, first_step_size, self.min_area)
        all_map_dict = {"ebsd_1": sorted(new_grain_ids)}
        print()

        # Conduct additional mapping
        for i in range(1,len(self.ebsd_maps)):

            # Get information of first EBSD map
            pixel_grid_1 = self.ebsd_maps[i-1]["pixel_grid"]
            grain_map_1  = self.ebsd_maps[i-1]["grain_map"]
            id_list_1    = all_map_dict[f"ebsd_{i}"]

            # Get information of second EBSD map
            pixel_grid_2 = self.ebsd_maps[i]["pixel_grid"]
            grain_map_2  = self.ebsd_maps[i]["grain_map"]
            step_size_2  = self.ebsd_maps[i]["step_size"]
            id_list_2    = get_grain_ids(grain_map_2, step_size_2, self.min_area)

            # Conduct mapping
            map_dict_12 = map_ebsd(
                pixel_grid_1 = pixel_grid_1,
                pixel_grid_2 = pixel_grid_2,
                grain_map_1  = grain_map_1,
                grain_map_2  = grain_map_2,
                id_list_1    = id_list_1,
                id_list_2    = id_list_2,
            )

            # No grains could be mapped
            if map_dict_12 == None:
                raise ValueError("No mapping could be done!")

            # Redefine new grain IDs
            new_id_list_2 = []
            for id_1 in id_list_1:
                id_2 = map_dict_12[id_1] if id_1 in map_dict_12.keys() else NO_MAPPING
                new_id_list_2.append(id_2)
            all_map_dict[f"ebsd_{i+1}"] = new_id_list_2

            # Print progress
            first_ordinal = integer_to_ordinal(i)
            second_ordinal = integer_to_ordinal(i+1)
            print(f"  Mapped grains of {first_ordinal} map to {second_ordinal} map")
        
        # Only include mappable grains
        all_mappings = list(all_map_dict.keys())
        self.map_dict = dict(zip(all_map_dict.keys(), [[] for _ in range(len(all_mappings))]))
        for i in range(len(all_map_dict[all_mappings[0]])):
            map_list = [all_map_dict[mapping][i] for mapping in all_mappings]
            if not NO_MAPPING in map_list:
                for j, key in enumerate(self.map_dict.keys()):
                    self.map_dict[key].append(int(map_list[j]))
        print(f"  Finished mapping grains of added EBSD maps\n")

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

    def export_reorientation(self, reorientation_path:str) -> None:
        """
        Calculates and saves the reorientation trajectories of the mapped grains

        Parameters:
        * `reorientation_path`: Path to save the dictionary
        """
        reorientation_dict = self.__get_reorientation__()
        reorientation_path = get_file_path_exists(reorientation_path, "csv")
        dict_to_csv(reorientation_dict, reorientation_path)

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
        initial_x_size = len(self.ebsd_maps[0]["pixel_grid"][0])*self.ebsd_maps[0]["step_size"]

        # Iterate through EBSD maps
        for i, ebsd_map in enumerate(self.ebsd_maps):
            
            # Plot EBSD maps
            current_x_size = len(ebsd_map["pixel_grid"][0])*ebsd_map["step_size"]
            current_figure_x = figure_x*current_x_size/initial_x_size
            plotter = EBSDPlotter(ebsd_map["pixel_grid"], ebsd_map["grain_map"], ebsd_map["step_size"], current_figure_x)
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
            pixel_grid_list = [ebsd_map["pixel_grid"] for ebsd_map in self.ebsd_maps],
            grain_map_list  = [ebsd_map["grain_map"] for ebsd_map in self.ebsd_maps],
            step_size_list  = [ebsd_map["step_size"] for ebsd_map in self.ebsd_maps],
            map_dict        = self.map_dict,
            grain_id        = grain_id,
            ipf             = ipf
        )

    def plot_reorientation(self, plot_path:str, structure:str="fcc", direction:list=[1,0,0], id_list:list=None) -> None:
        """
        Plots the reorientation trajectories on an inverse pole figure

        Parameters:
        * `plot_path`: Path to save the plot
        * `structure`: Crystal structure ("bcc", "fcc")
        * `direction`: Direction to plot the IPF
        * `id_list`:   List of grain IDs to plot; if undefined, plots all mappable grains
        """

        # Initialise plotter
        lattice = get_lattice(structure)
        ipf = IPF(lattice)

        # Get reorientation trajectories
        reorientation_dict = self.__get_reorientation__()
        if id_list == None:
            id_list = [int(field.replace("g","").replace("_phi_1","")) for field in reorientation_dict.keys() if "phi_1" in field]
        else:
            id_list = [id for id in id_list if f"g{id}_phi_1" in reorientation_dict.keys()]

        # Initialise history
        num_points = len(reorientation_dict[list(reorientation_dict.keys())[0]])
        exp_history = [[] for _ in range(num_points)]
        
        # Get experimental history
        for id in id_list:
            phi_1 = reorientation_dict[f"g{id}_phi_1"]
            Phi   = reorientation_dict[f"g{id}_Phi"]
            phi_2 = reorientation_dict[f"g{id}_phi_2"]
            for i in range(num_points):
                exp_history[i].append([phi_1[i], Phi[i], phi_2[i]])

        # Get trajectories and plot
        exp_trajectories = get_trajectories(exp_history)
        ipf.plot_ipf_trajectory(exp_trajectories, direction, "plot", {"color": "darkgray", "linewidth": 2})
        ipf.plot_ipf_trajectory(exp_trajectories, direction, "arrow", {"color": "darkgray", "head_width": 0.01, "head_length": 0.015})
        for i, et in enumerate(exp_trajectories):
            ipf.plot_ipf_trajectory([[et[0]]], direction, "scatter", {"color": "darkgray", "s": 8**2})
            ipf.plot_ipf_trajectory([[et[0]]], direction, "text", {"color": "black", "fontsize": 8, "s": id_list[i]})

        # Save plot
        plot_path = get_file_path_exists(plot_path, "png")
        save_plot(plot_path)

    def __get_reorientation__(self) -> dict:
        """
        Calculates the reorientation trajectories of the mapped grains (rads)
        """

        # Initialise dictionary
        reorientation_dict = {}
        for grain_id in self.map_dict["ebsd_1"]:
            reorientation_dict[f"g{grain_id}_phi_1"] = []
            reorientation_dict[f"g{grain_id}_Phi"]   = []
            reorientation_dict[f"g{grain_id}_phi_2"] = []

        # Get reorientation trajectories
        for i, base_id in enumerate(self.map_dict["ebsd_1"]):
            grain_fields = [f"g{base_id}_{p}" for p in ["phi_1", "Phi", "phi_2"]]
            for j, ebsd_map in enumerate(self.ebsd_maps):
                grain_id = self.map_dict[f"ebsd_{j+1}"][i]
                orientation = ebsd_map["grain_map"][grain_id].get_orientation()
                orientation = deg_to_rad(list(orientation))
                for k in range(len(grain_fields)):
                    reorientation_dict[grain_fields[k]].append(orientation[k])

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
                grain_ids = sorted(list(ebsd_map["grain_map"].keys()))

            # Calculate areas
            step_size = ebsd_map["step_size"]
            step_area = math.pow(step_size, 2)
            area_list = [ebsd_map["grain_map"][grain_id].get_size()*step_area for grain_id in grain_ids]
            
            # Calculate centroids
            centroid_dict = get_centroids(ebsd_map["pixel_grid"])
            centroid_x_list = [centroid_dict[grain_id][0]*step_size for grain_id in grain_ids]
            centroid_y_list = [centroid_dict[grain_id][1]*step_size for grain_id in grain_ids]

            # Get orientations
            orientation_list = [ebsd_map["grain_map"][grain_id].get_orientation() for grain_id in grain_ids]
            phi_1_list = [deg_to_rad(o[0]) for o in orientation_list]
            Phi_list   = [deg_to_rad(o[1]) for o in orientation_list]
            phi_2_list = [deg_to_rad(o[2]) for o in orientation_list]

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

def get_grain_ids(grain_map:dict, step_size:float, min_area:float=None) -> list:
    """
    Gets the grain IDs and filter by area if defined

    Parameters:
    * `grain_map`: The mapping of IDs to grains
    * `step_size`: The step size
    * `min_area`:  The minimum area to include the grains
    
    Returns the list of grain IDs
    """
    grain_ids = list(grain_map.keys())
    if min_area != None:
        min_area_scaled = min_area / math.pow(step_size, 2)
        grain_ids = [grain_id for grain_id in grain_ids if grain_map[grain_id].get_size() > min_area_scaled]
    return sorted(grain_ids)
