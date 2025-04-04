"""
 Title:         Grain Plotter
 Description:   Plots grain changes
 Author:        Janzen Choi

"""

# Libraries
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from ebsd_mapper.maths.ipf_cubic import euler_to_rgb
from ebsd_mapper.helper.plotter import get_coordinate, get_positions, save_plot, get_boundary, get_boundaries
from ebsd_mapper.mapper.mapper import NO_MAPPING

def plot_grains_manual(plot_path:str, pixel_grid:list, grain_map:dict, step_size:float,
                       grain_ids:list, x_ticks:tuple, y_ticks:tuple, ipf:str="x"):
    """
    Plots grain changes
    
    Parameters:
    * `plot_path:   Path to the plot
    * `pixel_grid`: The pixel grid
    * `grain_map`:  The grain map
    * `step_size`:  The step size
    * `grain_ids`:  List of grain IDs to plot
    * `x_ticks`:    The horizontal ticks of the plot
    * `y_ticks`:    The vertical ticks of the plot
    * `ipf`:        IPF direction to plot
    """
    
    # Initialise all coordinates
    all_x_list = []
    all_y_list = []

    # Initialise plot
    plt.figure(figsize=(5,5))
    plt.gca().set_aspect('equal', adjustable='box')
    plt.gca().set_position([0.17, 0.12, 0.75, 0.75])
    plt.gca().grid(which="major", axis="both", color="SlateGray", linewidth=1, linestyle=":", alpha=0.5)

    # Iterate through the grains
    for grain_id in grain_ids:

        # Get coordinates of the grain
        col_list, row_list = get_positions(grain_id, pixel_grid)
        x_list = [get_coordinate(col, step_size) for col in col_list]
        y_list = [get_coordinate(row, step_size) for row in row_list]

        # Get colour
        orientation = grain_map[grain_id].get_orientation()
        colour = [rgb/255 for rgb in euler_to_rgb(*orientation, ipf=ipf)]

        # Plot each pixel of the grain
        for x, y in zip(x_list, y_list):
            coordinates = [(x-step_size/2,y-step_size/2), (x-step_size/2,y+step_size/2),
                           (x+step_size/2,y+step_size/2), (x+step_size/2,y-step_size/2),]
            polygon = patches.Polygon(coordinates, closed=True, fill=True, facecolor=colour)
            plt.gca().add_patch(polygon)

        # Append coordinates to all coordinates
        all_x_list += x_list
        all_y_list += y_list

    # Plot the grains' boundaries
    bnd_x_list = []
    bnd_y_list = []
    for row in range(len(pixel_grid)):
        for col in range(len(pixel_grid[row])):
            if pixel_grid[row][col] in grain_ids:
                bnd_x, bnd_y = get_boundaries(row, col, pixel_grid, step_size, grain_ids)
                bnd_x_list += bnd_x
                bnd_y_list += bnd_y
    plt.plot(bnd_x_list, bnd_y_list, linewidth=1, color="black")

    # Format and save the plot
    if x_ticks != None:
        plt.xticks(x_ticks, x_ticks)
        plt.xlim(min(x_ticks), max(x_ticks))
    if y_ticks != None:
        plt.yticks(y_ticks, y_ticks)
        plt.ylim(max(y_ticks), min(y_ticks))
    plt.savefig(plot_path, dpi=300, bbox_inches="tight", pad_inches=0.2)
    plt.cla()
    plt.clf()
    plt.close()

def plot_grain_evolution_separate(plot_path:str, pixel_grid_list:list, grain_map_list:list,
                                  step_size_list:list, map_dict:dict, grain_id:int, ipf:str="x",
                                  white_space:bool=False):
    """
    Plots grain changes
    
    Parameters:
    * `plot_path:        Path to the plot
    * `pixel_grid_list`: List of pixel grids
    * `grain_map_list`:  List of grain maps
    * `step_size_list`:  List of step sizes
    * `map_dict`:        Dictionary of grain mappings across EBSD maps
    * `grain_id`:        Initial grain ID to display changes
    * `ipf`:             IPF direction to plot
    * `white_space`:     Whether to include white space in the plot
    """

    # Get grain mapping
    num_maps = len(pixel_grid_list)
    if num_maps > 1:
        grain_id_index = map_dict[list(map_dict.keys())[0]].index(grain_id)
        mapped_grain_id_list = [map_dict[key][grain_id_index] for key in map_dict.keys()]
    else:
        mapped_grain_id_list = [grain_id]
    
    # Get all pixel positions
    x_grid, y_grid = [], []
    for i in range(num_maps):
        
        # If no mapping is found, do not add coordinates
        if mapped_grain_id_list[i] == NO_MAPPING:
            x_grid.append([])
            y_grid.append([])
            continue
        
        # Otherwise, add coordinates of grain
        col_list, row_list = get_positions(int(mapped_grain_id_list[i]), pixel_grid_list[i])
        x_list = [get_coordinate(col, step_size_list[i]) for col in col_list]
        y_list = [get_coordinate(row, step_size_list[i]) for row in row_list]
        x_grid.append(x_list)
        y_grid.append(y_list)

    # Iterate through the maps
    for i in range(num_maps):
        
        # Check if the grain has mapping
        mapped_grain_index = mapped_grain_id_list[i]
        if mapped_grain_index == NO_MAPPING:
            continue

        # Initialise grain information
        pixel_grid = pixel_grid_list[i]
        grain_map  = grain_map_list[i]
        step_size  = step_size_list[i]
        x_list = x_grid[i]
        y_list = y_grid[i]

        # Initialise plot
        x_range = abs(max(x_list)-min(x_list))
        y_range = abs(max(y_list)-min(y_list))
        pixel_size = 0.1
        plt.figure(figsize=(x_range*pixel_size,y_range*pixel_size), dpi=100)
        plt.gca().set_aspect("equal", adjustable="datalim")

        # Get IPF colour
        orientation = grain_map[mapped_grain_index].get_orientation()
        colour = [rgb/255 for rgb in euler_to_rgb(*orientation, ipf=ipf)]

        # Plot each pixel of the grain
        for x, y in zip(x_list, y_list):
            coordinates = [(x-step_size/2,y-step_size/2), (x-step_size/2,y+step_size/2),
                        (x+step_size/2,y+step_size/2), (x+step_size/2,y-step_size/2),]
            polygon = patches.Polygon(coordinates, closed=True, fill=True, facecolor=colour)
            plt.gca().add_patch(polygon)

        # Draw boundaries
        boundary_x_list, boundary_y_list = [], []
        for j in range(len(x_list)):
            boundary_x, boundary_y = get_boundary(int(y_list[j]/step_size), int(x_list[j]/step_size), pixel_grid, step_size)
            boundary_x_list += boundary_x
            boundary_y_list += boundary_y
        plt.gca().plot(boundary_x_list, boundary_y_list, linewidth=10, color="black")

        # Format and save
        plt.gca().invert_yaxis()
        settings = {}
        if not white_space:
            plt.axis("off")
            settings = {"bbox_inches": "tight", "pad_inches": 0, "transparent": True}
        else:
            plt.gca().set_title(f"ebsd_{i+1}", fontsize=11)
        save_plot(f"{plot_path}_i{i+1}.png", settings)

def plot_grain_evolution(plot_path:str, pixel_grid_list:list, grain_map_list:list,
                         step_size_list:list, map_dict:dict, grain_id:int, ipf:str="x",
                         white_space:bool=False):
    """
    Plots grain changes
    
    Parameters:
    * `plot_path:        Path to the plot
    * `pixel_grid_list`: List of pixel grids
    * `grain_map_list`:  List of grain maps
    * `step_size_list`:  List of step sizes
    * `map_dict`:        Dictionary of grain mappings across EBSD maps
    * `grain_id`:        Initial grain ID to display changes
    * `ipf`:             IPF direction to plot
    * `white_space`:     Whether to include white space in the plot
    """

    # Get grain mapping
    num_maps = len(pixel_grid_list)
    if num_maps > 1:
        grain_id_index = map_dict[list(map_dict.keys())[0]].index(grain_id)
        mapped_grain_id_list = [map_dict[key][grain_id_index] for key in map_dict.keys()]
    else:
        mapped_grain_id_list = [grain_id]
    
    # Get all pixel positions
    x_grid, y_grid = [], []
    for i in range(num_maps):
        
        # If no mapping is found, do not add coordinates
        if mapped_grain_id_list[i] == NO_MAPPING:
            x_grid.append([])
            y_grid.append([])
            continue
        
        # Otherwise, add coordinates of grain
        col_list, row_list = get_positions(int(mapped_grain_id_list[i]), pixel_grid_list[i])
        x_list = [get_coordinate(col, step_size_list[i]) for col in col_list]
        y_list = [get_coordinate(row, step_size_list[i]) for row in row_list]
        x_grid.append(x_list)
        y_grid.append(y_list)

    # Calculate ranges of values
    buffer = 2
    all_min_x = min([min(x_list)-step_size_list[i]*buffer for i, x_list in enumerate(x_grid) if len(x_list) > 0])
    all_max_x = max([max(x_list)+step_size_list[i]*buffer for i, x_list in enumerate(x_grid) if len(x_list) > 0])
    all_min_y = min([min(y_list)-step_size_list[i]*buffer for i, y_list in enumerate(y_grid) if len(y_list) > 0])
    all_max_y = max([max(y_list)+step_size_list[i]*buffer for i, y_list in enumerate(y_grid) if len(y_list) > 0])
    x_range = all_max_x - all_min_x
    y_range = all_max_y - all_min_y

    # Initialise figure
    subplot_width = 2
    figure_gap = 0.8
    subplot_height = subplot_width*y_range/x_range
    subplot_size = math.ceil(math.sqrt(num_maps))
    figure_width = subplot_size * subplot_width + (subplot_size+1) * figure_gap
    figure_height = subplot_size * subplot_height + (subplot_size+1) * figure_gap
    subplot_positions = get_subplot_positions(subplot_size, subplot_width, subplot_height,
                                              figure_gap, figure_width, figure_height)
    figure = plt.figure(figsize=(figure_width, figure_height))

    # Iterate through the maps
    for i in range(num_maps):
        
        # Get information for this subplot
        axis = figure.add_axes(subplot_positions[i])
        pixel_grid = pixel_grid_list[i]
        grain_map  = grain_map_list[i]
        step_size  = step_size_list[i]
        mapped_grain_index = mapped_grain_id_list[i]
        x_list = x_grid[i]
        y_list = y_grid[i]

        # Only plot if there is a mapping
        if mapped_grain_id_list[i] != NO_MAPPING:

            # Get IPF colour
            orientation = grain_map[mapped_grain_index].get_orientation()
            colour = [rgb/255 for rgb in euler_to_rgb(*orientation, ipf=ipf)]

            # Plot the pixels
            square_size = 65*subplot_width*step_size/(max(x_list)-min(x_list)+2*buffer*step_size)
            axis.scatter(x_list, y_list, color=colour, s=square_size**2, marker="s")

            # Draw boundaries
            boundary_x_list, boundary_y_list = [], []
            for j in range(len(x_list)):
                boundary_x, boundary_y = get_boundary(int(y_list[j]/step_size), int(x_list[j]/step_size), pixel_grid, step_size)
                boundary_x_list += boundary_x
                boundary_y_list += boundary_y
            axis.plot(boundary_x_list, boundary_y_list, linewidth=1, color="black")

        # Add text and format axis
        axis.set_title(f"ebsd_{i+1}", fontsize=11)
        axis.invert_yaxis()
        axis.set_xlim(all_min_x, all_max_x)
        axis.set_ylim(all_max_y, all_min_y)

    # Format and save
    settings = {}
    if not white_space:
        plt.axis("off")
        settings = {"bbox_inches": "tight", "pad_inches": 0, "transparent": True}
    save_plot(f"{plot_path}.png", settings)

def get_subplot_positions(subplot_size:float, subplot_width:float, subplot_height:float,
                          figure_gap:float, figure_width:float, figure_height:float) -> list:
    """
    Calculates the positions of the subplots
    
    Parameters:
    * `subplot_size`:   The number of the subplots on each axis
    * `subplot_width`:  The width of the subplots
    * `subplot_height`: The height of the subplots
    * `figure_gap`:     The gap between the subplots
    * `figure_width`:   The width of the figure
    * `figure_height`:  The height of the figure
    
    Returns the list of positions of the subplots
    """
    positions = []
    for i in range(subplot_size):
        for j in range(subplot_size):
            left = j * (subplot_width + figure_gap) / figure_width + figure_gap / figure_width
            bottom = 1 - (i + 1) * (subplot_height + figure_gap) / figure_height
            width = subplot_width / figure_width
            height = subplot_height / figure_height
            positions.append([left, bottom, width, height])
    return positions
