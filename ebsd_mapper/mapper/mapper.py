"""
 Title:         Mapper
 Description:   Maps the grains in multiple EBSD maps
 Author:        Janzen Choi

"""

# Libraries
import math
from ebsd_mapper.mapper.edge import Edge
from ebsd_mapper.helper.general import integer_to_ordinal
from ebsd_mapper.maths.orientation import get_geodesic, deg_to_rad

# Constants
NO_MAPPING = ""

# Mapper class
class Mapper:

    def __init__(self, ebsd_maps:list, radius:float, min_area:float=None) -> dict:
        """
        Initialises the Mapper class
        
        Parameters:
        * `ebsd_maps`: List of Map objects
        * `radius`:    Radius to conduct the mapping; 1.0 covers most of the map
        * `min_area`:  The minimum area to include the grains
        """
        
        # Initialise internal variables
        self.ebsd_maps = ebsd_maps
        self.radius = radius
        self.min_area = min_area
        
        # Conduct initial calculations
        self.grain_ids_list = [self.ebsd_maps[0].get_grain_ids(self.min_area)]
        self.centroid_dict_list = [ebsd_map.get_norm_centroids() for ebsd_map in self.ebsd_maps]

    def get_viable_centroid(self, grain_id:int) -> tuple:
        """
        Gets the latest mapped centroid
        
        Parameters:
        * `grain_id`: The grain ID
        
        Returns the coordinates of the centroid
        """

        # Checks that the grain ID exists
        if not grain_id in self.grain_ids_list[0]:
            raise ValueError("Grain ID not found!")

        # Iterate backwards through mappings to find latest mapping
        grain_id_index = self.grain_ids_list[0].index(grain_id)
        for i in range(len(self.grain_ids_list))[::-1]:
            if self.grain_ids_list[i][grain_id_index] != "":
                centroid = self.centroid_dict_list[i][grain_id]
                return centroid

    def link_adjacent(self) -> dict:
        """
        Maps the grains between adjacent ebsd maps;
        Returns a dictionary mapping the grain IDs
        """
        
        # Get information about previous EBSD map
        num_mapped = len(self.grain_ids_list)
        prev_ebsd_map = self.ebsd_maps[num_mapped-1]
        prev_grain_ids = self.grain_ids_list[num_mapped-1]
        prev_centroid_dict = self.centroid_dict_list[num_mapped-1]
        
        # Get information about current EBSD map
        curr_ebsd_map = self.ebsd_maps[num_mapped]
        curr_grain_ids = self.ebsd_maps[num_mapped].get_grain_ids(self.min_area)
        curr_centroid_dict = self.centroid_dict_list[num_mapped]
        
        # Create a list of edges between grain IDs
        edge_list = []
        for prev_grain_id in prev_grain_ids:
            for curr_grain_id in curr_grain_ids:
                
                # Calculate centroid error
                pc = prev_centroid_dict[prev_grain_id]
                cc = curr_centroid_dict[curr_grain_id]
                centroid_error = math.sqrt(math.pow(pc[0]-cc[0],2) + math.pow(pc[1]-cc[1],2))
        
                # Eliminate mappings outside of radius
                if centroid_error > self.radius:
                    continue
        
                # Calculate orientation error
                euler_1 = deg_to_rad(list(prev_ebsd_map.get_grain(prev_grain_id).get_orientation()))
                euler_2 = deg_to_rad(list(curr_ebsd_map.get_grain(curr_grain_id).get_orientation()))
                orientation_error = get_geodesic(euler_1, euler_2)
                
                # Create edge and append
                edge = Edge(prev_grain_id, curr_grain_id)
                edge.add_error(centroid_error)
                edge.add_error(orientation_error)
                edge_list.append(edge)
        
        # Initialise mapping
        weight_list = [edge.get_weight() for edge in edge_list]
        sorted_weight_list = sorted(weight_list)
        grain_id_map = {}
        
        # Conduct mapping by using minimum edge combination between two disjoint sets of nodes
        for weight in sorted_weight_list:
            edge = edge_list[weight_list.index(weight)]
            if edge.get_node_1() in grain_id_map.keys() or edge.get_node_2() in grain_id_map.values():
                continue
            grain_id_map[edge.get_node_1()] = edge.get_node_2()
            
        # Return grain ID map
        return grain_id_map
        
    def link_ebsd_maps(self) -> dict:
        """
        Maps the grains of EBSD maps;
        Returns a dictionary mapping the grain IDs of the EBSD maps
        """
        
        # Map through all maps
        print()
        for i in range(len(self.ebsd_maps)-1):
            
            # Link current and previous map
            grain_id_map = self.link_adjacent()
            
            # Iterate through previous grain IDs
            prev_grain_ids = self.grain_ids_list[-1]
            curr_grain_ids = []
            for prev_grain_id in prev_grain_ids:
                if prev_grain_id in grain_id_map.keys():
                    curr_grain_ids.append(grain_id_map[prev_grain_id])
                else:
                    curr_grain_ids.append(NO_MAPPING)
            
            # Add to list of grain ID mappings
            self.grain_ids_list.append(curr_grain_ids)
            
            # Print progress
            first_ordinal = integer_to_ordinal(i+1)
            second_ordinal = integer_to_ordinal(i+2)
            print(f"  Mapped grains of {first_ordinal} map to {second_ordinal} map")
        
        # Create and return dictionary of all grain ID mappings
        print()
        map_dict = {}
        for i, grain_ids in enumerate(self.grain_ids_list):
            map_dict[f"ebsd_{i+1}"] = grain_ids
        return map_dict
