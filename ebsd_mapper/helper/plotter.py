"""
 Title:         Plotter
 Description:   Helper functions for the plotter
 Author:        Janzen Choi

"""

# Libraries
import matplotlib.pyplot as plt
import numpy as np

def get_boundaries(row:int, col:int, pixel_grid:list, step_size:float, grain_ids:list) -> tuple:
    """
    Gets coordinates for drawing the boundaries

    Parameters:
    * `row`:        The row of the pixel
    * `col`:        The column of the pixel
    * `pixel_grid`: The grid of pixels
    * `step_size`:  The step size
    * `grain_ids`:  List of grain IDs to get boundaries for

    Returns the x and y lists
    """

    # Initialise
    x_list, y_list = [], []
    x = get_coordinate(col, step_size)
    y = get_coordinate(row, step_size)
    
    # Check to add boundary on the right
    if col+1 >= len(pixel_grid[0]) or not pixel_grid[row][col+1] in grain_ids:
        x_list += [x + step_size/2]*2 + [np.NaN]
        y_list += [y - step_size/2, y + step_size/2] + [np.NaN]

    # Check to add boundary on the left
    if col-1 < 0 or not pixel_grid[row][col-1] in grain_ids:
        x_list += [x - step_size/2]*2 + [np.NaN]
        y_list += [y - step_size/2, y + step_size/2] + [np.NaN]

    # Check to add boundary on the top
    if row+1 >= len(pixel_grid) or not pixel_grid[row+1][col] in grain_ids:
        x_list += [x - step_size/2, x + step_size/2] + [np.NaN]
        y_list += [y + step_size/2]*2 + [np.NaN]

    # Check to add boundary on the bottom
    if row-1 < 0 or not pixel_grid[row-1][col] in grain_ids:
        x_list += [x - step_size/2, x + step_size/2] + [np.NaN]
        y_list += [y - step_size/2]*2 + [np.NaN]

    # Return the coordinates
    return x_list, y_list

def get_boundary(row:int, col:int, pixel_grid:list, step_size:float) -> tuple:
    """
    Gets coordinates for drawing the boundaries

    Parameters:
    * `row`:        The row of the pixel
    * `col`:        The column of the pixel
    * `pixel_grid`: The grid of pixels
    * `step_size`:  The step size

    Returns the x and y lists
    """

    # Initialise
    x_list, y_list = [], []
    x = get_coordinate(col, step_size)
    y = get_coordinate(row, step_size)
    
    # Check to add boundary on the right
    if col+1 >= len(pixel_grid[0]) or pixel_grid[row][col] != pixel_grid[row][col+1]:
        x_list += [x + step_size/2]*2 + [np.NaN]
        y_list += [y - step_size/2, y + step_size/2] + [np.NaN]

    # Check to add boundary on the left
    if col-1 < 0 or pixel_grid[row][col] != pixel_grid[row][col-1]:
        x_list += [x - step_size/2]*2 + [np.NaN]
        y_list += [y - step_size/2, y + step_size/2] + [np.NaN]

    # Check to add boundary on the top
    if row+1 >= len(pixel_grid) or pixel_grid[row][col] != pixel_grid[row+1][col]:
        x_list += [x - step_size/2, x + step_size/2] + [np.NaN]
        y_list += [y + step_size/2]*2 + [np.NaN]

    # Check to add boundary on the bottom
    if row-1 < 0 or pixel_grid[row][col] != pixel_grid[row-1][col]:
        x_list += [x - step_size/2, x + step_size/2] + [np.NaN]
        y_list += [y - step_size/2]*2 + [np.NaN]

    # Return the coordinates
    return x_list, y_list

def get_coordinate(index:int, step_size:float) -> float:
    """
    Converts an index into a coordinate value

    Parameters:
    * `index`:     The index
    * `step_size`: The step size

    Returns the coordinate value
    """
    return index*step_size + step_size/2

def get_positions(grain_id:int, pixel_grid:list) -> tuple:
    """
    Gets the positions of a grain in a pixel grid

    Parameters:
    * `grain_id`:   The ID of the grain
    * `pixel_grid`: The grid of pixels

    Returns the column and row positions
    """
    col_list, row_list = [], []
    for row in range(len(pixel_grid)):
        for col in range(len(pixel_grid[row])):
            if grain_id == pixel_grid[row][col]:
                col_list.append(col)
                row_list.append(row)
    return col_list, row_list

def define_legend(colour_list:list, label_list:list, type_list:list) -> None:
    """
    Manually defines the plot legend
    
    Parameters:
    * `colour_list`: The colours in the legend
    * `label_list`:  The keys to add to the legend
    * `type_list`:   The type of the icons in the legend
    """
    for i in range(len(colour_list)):
        if type_list[i] == "scatter":
            plt.scatter([], [], color=colour_list[i], label=label_list[i], s=7**2)
        elif type_list[i] == "line":
            plt.plot([], [], color=colour_list[i], label=label_list[i], linewidth=2)
    plt.legend(framealpha=1, edgecolor="black", fancybox=True, facecolor="white")

def save_plot(file_path:str, settings:dict={}) -> None:
    """
    Saves the plot and clears the figure

    Parameters:
    * `file_path`: The path to save the plot
    * `settings`:  Settings for the `savefig` function
    """
    plt.savefig(file_path, **settings)
    plt.cla()
    plt.clf()
    plt.close()
