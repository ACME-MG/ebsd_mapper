"""
 Title:         Interface
 Description:   Interface for mapping grains between EBSD maps
 Author:        Janzen Choi

"""

# Libraries
import inspect, re, time
from ebsd_mapper.mapper.controller import Controller
from ebsd_mapper.helper.general import integer_to_ordinal
from ebsd_mapper.helper.io import safe_mkdir, dict_to_csv

# Interface Class
class Interface:

    def __init__(self, title:str="", output_path:str="./results", verbose:bool=True, output_here:bool=False):
        """
        Class to interact with the optimisation code
        
        Parameters:
        * `title`:       Title of the output folder
        * `input_path`:  Path to the input folder
        * `output_path`: Path to the output folder
        * `verbose`:     If true, outputs messages for each function call
        * `output_here`: If true, just dumps the output in ths executing directory
        """

        # Initialise internal variables
        self.__print_index__ = 0
        self.__verbose__     = verbose
        self.__controller__  = Controller()
        self.__controller__.define_headers("x", "y", "grain_id", "phi_1", "Phi", "phi_2")
        
        # Print starting message and get start time
        time_str = time.strftime("%A, %D, %H:%M:%S", time.localtime())
        self.__print__(f"\n  Starting on {time_str}\n", add_index=False)
        self.__start_time__ = time.time()
        time_stamp = time.strftime("%y%m%d%H%M%S", time.localtime(self.__start_time__))
        
        # Define input and output
        file_path = inspect.currentframe().f_back.f_code.co_filename
        file_name = file_path.split("/")[-1].replace(".py","")
        title = f"_{file_name}" if title == "" else f"_{title}"
        title = re.sub(r"[^a-zA-Z0-9_]", "", title.replace(" ", "_"))
        output_dir = "." if output_here else f"{output_path}/{time_stamp}{title}"
        self.__get_output__ = lambda x : f"{output_dir}/{x}"
        
        # Create directories
        if not output_here:
            safe_mkdir(output_path)
            safe_mkdir(output_dir)

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
        self.__print__("Defining headers for EBSD files")
        self.__controller__.define_headers(x, y, grain_id, phi_1, Phi, phi_2)

    def import_ebsd(self, ebsd_path:str, step_size:float) -> None:
        """
        Reads in an EBSD map

        Parameters:
        * `ebsd_path`: Path to the EBSD file as a CSV file
        * `step_size`: Step size between coordinates
        """
        ordinal = integer_to_ordinal(len(self.__controller__.ebsd_maps)+1)
        self.__print__(f"Adding {ordinal} EBSD map")
        self.__controller__.import_ebsd(ebsd_path, step_size)

    def get_bounds(self) -> dict:
        """
        Returns the bounds of the most recently imported EBSD map
        """
        self.__print__(f"Getting the bounds of the EBSD map")
        bounds = self.__controller__.get_bounds()
        return bounds

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
        self.__print__("Redefining the domain of most recently imported EBSD map")
        self.__check_ebsd__()
        self.__controller__.rebound_ebsd(x_min, x_max, y_min, y_max)

    def map_ebsd(self, min_area:float=1e7, radius:float=1.0, tolerance:float=1.0,
                 export_errors:bool=False) -> None:
        """
        Maps the grains of the EBSD maps that have been read in
        
        Parameters:
        * `min_area`:      The minimum area of the grains to do the mapping
        * `radius`:        The radius to do the mapping; (1.0 covers most of the map)
        * `tolerance`:     The maximum error to allow for a mapping (1.0 allows most errors)
        * `export_errors`: Whether to export the errors or not
        """
        self.__check_ebsd__(2)
        self.__print__(f"Mapping the grains of EBSD maps")
        error_dict = self.__controller__.map_ebsd(radius, tolerance)
        if export_errors:
            dict_to_csv(error_dict, self.__get_output__("map_errors.csv"))

    def import_map(self, map_path:str) -> None:
        """
        Reads the grain mapping dictionary outputted by the script;
        saves time on remapping the EBSD maps

        Parameters:
        * `map_path`: The path to the mapping dictionary
        """
        self.__print__(f"Importing map from '{map_path}'")
        self.__controller__.import_map(map_path)

    def plot_ebsd(self, ebsd_path:str="ebsd", ipf:str="x", figure_x:float=10,
                  grain_id:bool=False, boundary:bool=False, id_list:list=None) -> None:
        """
        Plots the EBSD maps

        Parameters:
        * `ebsd_path`: Path to save plot
        * `ipf`:       The IPF colour ("x", "y", "z")
        * `figure_x`:  The initial horizontal size of the figures
        * `grain_id`:  Whether to include IDs in the EBSD maps;
                       define dictionary for custom settings
        * `boundary`:  Whether to include IDs in the EBSD maps;
                       define dictionary for custom settings
        * `id_list`:   The IDs of the grains to plot the IDs and boundaries;
                       IDs are the ones of the first grain map;
                       if undefined, adds for all grains
        """
        num_maps = len(self.__controller__.ebsd_maps)
        self.__print__(f"Plotting {num_maps} EBSD map(s)")
        self.__check_ebsd__(1)
        ebsd_path = self.__get_output__(ebsd_path)
        self.__controller__.plot_ebsd(ebsd_path, ipf, figure_x, grain_id, boundary, id_list)

    def plot_grain(self, grain_id:int, plot_path:str="grain_plot", ipf:str="x") -> None:
        """
        Plots changes to a single grain

        Parameter:
        * `grain_id`: The grain ID
        * `plot_path: Path to the plot (without extension)
        * `ipf`:      The IPF colour ("x", "y", "z")
        """
        self.__print__(f"Plotting changes to grain {grain_id}")
        self.__check_ebsd__(1)
        if len(self.__controller__.ebsd_maps) > 1:
            self.__check_mapping__()
        if not grain_id in self.__controller__.map_dict["ebsd_1"]:
            raise ValueError(f"The grain id of '{grain_id}' is not mappable!")
        plot_path = self.__get_output__(f"{plot_path}_{grain_id}")
        self.__controller__.plot_grain(grain_id, plot_path, ipf)

    def export_stats(self, stats_path:str="stats", sort_stat:str="grain_id", stats:list=None, add_header:bool=True, descending:bool=False) -> None:
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
        self.__print__("Exporting the statistics of the EBSD map(s)")
        self.__check_ebsd__(1)
        available_stats = ["grain_id", "area", "centroid_x", "centroid_y", "phi_1", "Phi", "phi_2"]
        stats = stats if stats != None else available_stats
        for stat in stats + [sort_stat]:
            if not stat in available_stats:
                raise ValueError(f"The '{stat}' statistic is not one of the available statistics that can be !")
        stats_path = self.__get_output__(stats_path)
        self.__controller__.export_stats(stats_path, sort_stat, stats, add_header, descending)

    def export_map(self, map_path:str="grain_map") -> None:
        """
        Exports the grain mapping dictionary as a CSV file

        Parameters:
        * `map_path`: Path to save the dictionary (without extension)
        """
        self.__print__("Exporting the grain mapping")
        self.__check_mapping__()
        map_path = self.__get_output__(map_path)
        self.__controller__.export_map(map_path)

    def export_reorientation(self, reorientation_path:str="reorientation") -> None:
        """
        Exports the reorientation trajectories of the mapped grains

        Parameters:
        * `reorientation_path`: Path to save the dictionary (without extension)
        """
        self.__print__("Exporting reorientation trajectories of mapped grains")
        self.__check_mapping__()
        reorientation_path = self.__get_output__(reorientation_path)
        self.__controller__.export_reorientation(reorientation_path)

    def plot_reorientation(self, plot_path:str="reorientation", structure:str="fcc", direction:list=[1,0,0], id_list:list=None) -> None:
        """
        Plots the reorientation trajectories on an inverse pole figure

        Parameters:
        * `plot_path`: Path to save the plot (without extension)
        * `structure`: Crystal structure ("bcc", "fcc")
        * `direction`: Direction to plot the IPF
        * `id_list`:   List of grain IDs to plot; if undefined, plots all mappable grains
        """
        self.__print__("Plotting the reorientation trajectories of mapped grains")
        plot_path = self.__get_output__(plot_path)
        self.__controller__.plot_reorientation(plot_path, structure, direction, id_list)

    def __check_ebsd__(self, min_maps:int=0) -> None:
        """
        Checks that at least one EBSD map has been read in

        Parameters:
        * `min_maps`: The minimum number of maps required
        """
        num_maps = len(self.__controller__.ebsd_maps)
        if num_maps < min_maps:
            if min_maps <= 1:
                raise ValueError("No EBSD maps have been added yet!")
            else:
                raise ValueError("Insufficient EBSD maps added!")

    def __check_mapping__(self) -> None:
        """
        Checks that the mapping has been done
        """
        if len(self.__controller__.map_dict.keys()) == 0:
            raise ValueError("The mapping has not been conducted!")
        if len(self.__controller__.map_dict.keys()) != len(self.__controller__.ebsd_maps):
            raise ValueError("The number of EBSD maps added does not match the mapping!")

    def __print__(self, message:str, add_index:bool=True, sub_index:bool=False) -> None:
        """
        Displays a message before running the command (for internal use only)
        
        Parameters:
        * `message`:   the message to be displayed
        * `add_index`: if true, adds a number at the start of the message
        * `sub_index`: if true, adds a number as a decimal
        """
        
        # Special printing cases
        if not self.__verbose__:
            return
        if not add_index:
            print(message)
            return
        
        # Prints with an index / subindex
        if sub_index:
            self.__print_subindex__ += 1
            print_index = f"     {self.__print_index__}.{self.__print_subindex__}"
        else:
            self.__print_index__ += 1
            self.__print_subindex__ = 0
            print_index = f"{self.__print_index__}"
        print(f"   {print_index})\t{message} ...")

    def __del__(self):
        """
        Prints out the final message (for internal use only)
        """
        time_str = time.strftime("%A, %D, %H:%M:%S", time.localtime())
        duration = round(time.time() - self.__start_time__)
        duration_h = duration // 3600
        duration_m = (duration - duration_h * 3600) // 60
        duration_s = duration - duration_h * 3600 - duration_m * 60
        duration_str_list = [
            f"{duration_h} hours" if duration_h > 0 else "",
            f"{duration_m} mins" if duration_m > 0 else "",
            f"{duration_s} seconds" if duration_s > 0 else ""
        ]
        duration_str = ", ".join([d for d in duration_str_list if d != ""])
        duration_str = f"in {duration_str}" if duration_str != "" else ""
        self.__print__(f"\n  Finished on {time_str} {duration_str}\n", add_index=False)
