"""
 Title:         Optimiser Interface
 Description:   Interface for calibrating models
 Author:        Janzen Choi

"""

# Libraries
import re, time
from ebsd_mapper.mapping.controller import Controller
from ebsd_mapper.helper.general import integer_to_ordinal
from ebsd_mapper.helper.io import safe_mkdir

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
        title = "" if title == "" else f"_{title}"
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

    def add_ebsd(self, ebsd_path:str, step_size:float) -> None:
        """
        Adds an EBSD map

        Parameters:
        * `ebsd_path`: Path to the EBSD file as a CSV file
        * `step_size`: Step size between coordinates
        """
        ordinal = integer_to_ordinal(len(self.__controller__.ebsd_maps)+1)
        self.__print__(f"Adding {ordinal} EBSD map")
        self.__controller__.add_ebsd(ebsd_path, step_size)

    def plot_ebsd(self, ipf:str="x", figure_x:float=10,
                  include_id:bool=False, include_boundary:bool=False, id_list:list=None) -> None:
        """
        Plots the EBSD maps

        Parameters:
        * `ipf`:              The IPF colour ("x", "y", "z")
        * `figure_x`:         The horizontal size of the figures
        * `include_id`:       Whether to include IDs in the EBSD maps;
                              define dictionary for custom settings
        * `include_boundary`: Whether to include IDs in the EBSD maps;
                              define dictionary for custom settings
        * `id_list`:          The IDs of the grains to add the IDs and boundaries;
                              IDs are the ones of the first grain map;
                              if undefined, adds for all grains
        """
        num_maps = len(self.__controller__.ebsd_maps)
        self.__print__(f"Plotting {num_maps} EBSD map(s)")
        ebsd_path = self.__get_output__("ebsd")
        self.__controller__.plot_ebsd(ebsd_path, ipf, figure_x, include_id, include_boundary, id_list)

    def export_map(self) -> None:
        """
        Exports the grain mapping dictionary
        """
        self.__print__("Exporting the grain mapping")
        map_path = self.__get_output__("grain_map")
        self.__controller__.export_map(map_path)

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
