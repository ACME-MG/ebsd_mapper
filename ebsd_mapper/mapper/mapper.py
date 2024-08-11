"""
 Title:         Mapper
 Description:   Maps the grains in multiple EBSD maps
 Author:        Janzen Choi

"""

# Libraries
import math, time
from ebsd_mapper.mapper.edge import Edge
from ebsd_mapper.helper.general import integer_to_ordinal, transpose, round_sf
from ebsd_mapper.maths.orientation import deg_to_rad
from ebsd_mapper.maths.neml import get_cubic_misorientation

# Constants
NO_MAPPING = -1

# Mapper class
class Mapper:

    def __init__(self, ebsd_maps:list, radius:float, min_area:float, tolerance:float) -> dict:
        """
        Initialises the Mapper class
        
        Parameters:
        * `ebsd_maps`: List of Map objects
        * `radius`:    Radius to conduct the mapping; 1.0 covers most of the map
        * `min_area`:  The minimum area to include the grains
        * `tolerance`: The maximum error to allow for a mapping
        """
        
        # Initialise internal variables
        self.ebsd_maps = ebsd_maps
        self.radius    = radius
        self.min_area  = min_area
        self.tolerance = tolerance
        
        # Get information about first grain map
        grain_ids = self.ebsd_maps[0].get_grain_ids(self.min_area)
        centroid_dict = self.ebsd_maps[0].get_norm_centroids()
        grain_map = self.ebsd_maps[0].get_grain_map()
        
        # Initialise history
        self.history = {
            "grain_ids":    [[grain_id] for grain_id in grain_ids],
            "centroids":    [[centroid_dict[grain_id]] for grain_id in grain_ids],
            "orientations": [[grain_map[grain_id].get_orientation()] for grain_id in grain_ids],
            "errors":       [[NO_MAPPING] for _ in grain_ids]
        }

    def link_adjacent(self) -> dict:
        """
        Maps the grains between adjacent ebsd maps;
        Returns a dictionary mapping the grain IDs
        """
        
        # Get information about previous EBSD map
        prev_centroids = [centroids[-1] for centroids in self.history["centroids"]]
        prev_orientations = [orientations[-1] for orientations in self.history["orientations"]]
        
        # Get information about current EBSD map
        num_mapped         = len(self.history["grain_ids"][0])
        curr_ebsd_map      = self.ebsd_maps[num_mapped]
        curr_grain_ids     = curr_ebsd_map.get_grain_ids(self.min_area)
        curr_centroid_dict = curr_ebsd_map.get_norm_centroids()
        curr_centroids     = [curr_centroid_dict[grain_id] for grain_id in curr_grain_ids]
        curr_orientations  = [curr_ebsd_map.get_grain(grain_id).get_orientation() for grain_id in curr_grain_ids]

        # Create a list of edges between grain IDs
        edge_list = []
        for i in range(len(prev_centroids)):
            for j in range(len(curr_centroids)):
                
                # Calculate centroid error
                pc = prev_centroids[i]
                cc = curr_centroids[j]
                centroid_error = math.sqrt(math.pow(pc[0]-cc[0],2) + math.pow(pc[1]-cc[1],2))
        
                # Eliminate mappings outside of radius
                if centroid_error > self.radius:
                    continue
        
                # Calculate orientation error
                euler_1 = deg_to_rad(list(prev_orientations[i]))
                euler_2 = deg_to_rad(list(curr_orientations[j]))
                orientation_error = get_cubic_misorientation(euler_1, euler_2)
                
                # Create edge and append if under tolerance
                edge = Edge(i, j)
                edge.add_error(centroid_error)
                edge.add_error(orientation_error)
                if edge.get_weight() < self.tolerance:
                    edge_list.append(edge)

        # Initialise mapping
        weight_list = [edge.get_weight() for edge in edge_list]
        sorted_weight_list = sorted(weight_list)
        index_map = {}
        error_map = {}
        
        # Conduct mapping by using minimum edge combination between two disjoint sets of nodes
        for weight in sorted_weight_list:
            edge = edge_list[weight_list.index(weight)]
            if edge.get_node_1() in index_map.keys() or edge.get_node_2() in index_map.values():
                continue
            index_map[edge.get_node_1()] = edge.get_node_2()
            error_map[edge.get_node_1()] = edge.get_weight()
        
        # Iterate through indexes
        for i in range(len(prev_centroids)):
                
            # If grain is mappable, then add new grain information to chain
            if i in index_map.keys():
                new_index = index_map[i]
                self.history["grain_ids"][i].append(int(curr_grain_ids[new_index]))
                self.history["centroids"][i].append(curr_centroids[new_index])
                self.history["orientations"][i].append(curr_orientations[new_index])
                self.history["errors"][i].append(error_map[i])
            
            # Otherwise, add old grain information to chain
            else:
                self.history["grain_ids"][i].append(NO_MAPPING)
                self.history["centroids"][i].append(self.history["centroids"][i][-1])
                self.history["orientations"][i].append(self.history["orientations"][i][-1])
                self.history["errors"][i].append(NO_MAPPING)

    def link_ebsd_maps(self) -> dict:
        """
        Maps the grains of EBSD maps;
        Returns a dictionary mapping the grain IDs of the EBSD maps
        """
        
        # Map grains of all maps
        print()
        for i in range(len(self.ebsd_maps)-1):
            start_time = time.time()
            self.link_adjacent()
            first_ordinal = integer_to_ordinal(i+1)
            second_ordinal = integer_to_ordinal(i+2)
            duration = round_sf(time.time()-start_time, 2)
            print(f"  Mapped grains of {first_ordinal} map to {second_ordinal} map ({duration}s)")
        print()
        
        # Create and return dictionary of all grain ID mappings
        grain_id_trajectories = transpose(self.history["grain_ids"])
        map_dict = {}
        for i, grain_id_trajectory in enumerate(grain_id_trajectories):
            map_dict[f"ebsd_{i+1}"] = grain_id_trajectory
        return map_dict

    def get_error_dict(self) -> dict:
        """
        Gets the errors after the mapping
        """
        error_dict = {"grain_id": [grain_ids[0] for grain_ids in self.history["grain_ids"]]}
        error_trajectories = transpose(self.history["errors"])[1:]
        for i, error_trajectory in enumerate(error_trajectories):
            error_dict[f"ebsd_{i+1}_to_{i+2}"] = error_trajectory
        return error_dict
