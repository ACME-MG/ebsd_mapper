"""
 Title:         Plotter
 Description:   Plots EBSD maps using a plot
 Author:        Janzen Choi

"""

# Libraries
import numpy as np
import matplotlib.pyplot as plt
from ebsd_mapper.mapping.gridder import get_centroids
from ebsd_mapper.maths.ipf_cubic import euler_to_rgb

# Plotter class
class Plotter:
    
    def __init__(self, pixel_grid:list, grain_map:dict, step_size:float, figure_x:float=10):
        """
        Constructor for the plotter class
        
        Parameters:
        * `pixel_grid`: A grid of pixels
        * `grain_map`:  A mapping of the grains to the average orientations
        * `step_size`:  The step size of the EBSD map
        * `figure_x`:   Size of the horizontal axis of the figure (in inches)
        """
        
        # Initialise internal variables
        self.pixel_grid = pixel_grid
        self.grain_map = grain_map
        self.step_size = step_size
        self.figure_x = figure_x
        
        # Initialise plot
        x_max = len(pixel_grid[0])*self.step_size
        y_max = len(pixel_grid)*self.step_size
        self.figure, self.axis = plt.subplots(figsize=(figure_x, y_max/x_max*figure_x))
        plt.xlim(0, x_max)
        plt.ylim(0, y_max)
        
        # Define size of each square marker (55 magical number)
        self.square_size = 55*self.figure_x*self.step_size/x_max

    def get_coordinate(self, index:int) -> float:
        """
        Converts an index into a coordinate value

        Parameters:
        * `index`: The index

        Returns the coordinate value
        """
        return index*self.step_size + self.step_size/2

    def plot_ebsd(self, ipf:str="x") -> None:
        """
        Plots the EBSD map using Matplotlib
        
        Parameters:
        * `pixel_grid`: A grid of pixels
        * `grain_map`:  A mapping of the grains to the average orientations
        * `step_size`:     The step size of the EBSD map
        * `ipf`:        The IPF direction
        """
        
        # Create colour map
        colour_map = {}
        for grain_id in self.grain_map.keys():
            orientation = self.grain_map[grain_id].get_orientation()
            colour = [rgb/255 for rgb in euler_to_rgb(*orientation, ipf=ipf)]
            colour_map[grain_id] = colour
        
        # Prepare pixel data
        x_list, y_list, colour_list = [], [], []
        for row in range(len(self.pixel_grid)):
            for col in range(len(self.pixel_grid[row])):
                if self.pixel_grid[row][col] in colour_map.keys():
                    x_list.append(self.get_coordinate(col))
                    y_list.append(self.get_coordinate(row))
                    colour_list.append(colour_map[self.pixel_grid[row][col]])

        # Plot
        plt.scatter(x_list, y_list, c=colour_list, s=self.square_size**2, marker="s")

    def plot_border(self) -> None:
        """
        Draws an outline at the outermost pixels;
        for checking that the whole microstructre is shown
        """
        x_list, y_list, colour_list = [], [], []
        for row in range(len(self.pixel_grid)):
            for col in range(len(self.pixel_grid[row])):
                if (col == 0 or col == len(self.pixel_grid[row])-1 or
                    row == 0 or row == len(self.pixel_grid)-1):
                        x_list.append(self.get_coordinate(col))
                        y_list.append(self.get_coordinate(row))
                        colour_list.append((0,0,0))
        plt.scatter(x_list, y_list, c=colour_list, s=self.square_size**2, marker="s")

    def plot_ids(self, id_list:list=None, settings:dict={}) -> None:
        """
        Writes the grain IDs at the centroids
        
        Parameters:
        * `id_list`: List of grain IDs to add centroids to
        """
        centroid_dict = get_centroids(self.pixel_grid)
        for grain_id in centroid_dict.keys():
            if id_list != None and not grain_id in id_list:
                continue
            x, y = centroid_dict[grain_id]
            x = self.get_coordinate(x)
            y = self.get_coordinate(y)
            plt.text(x, y, str(grain_id), ha="center", va="center", **settings)

    def plot_boundaries(self, id_list:list=None, settings:dict={}) -> None:
        """
        Plots the grain boundaries
        
        Parameters:
        * `id_list`: List of grain IDs to draw boundaries around
        """
        
        # Initialise
        x_size = len(self.pixel_grid[0])
        y_size = len(self.pixel_grid)
        x_list, y_list = [], []
        
        # Iterate through pixels
        for row in range(y_size):
            for col in range(x_size):
                
                # Only draw boundaries around specified grains (if specified)
                if (id_list != None and not self.pixel_grid[row][col] in id_list):
                    continue
                
                # Get coordinates for pixel
                x = self.get_coordinate(col)
                y = self.get_coordinate(row)
                
                # Check to add boundary on the right
                if col+1 < x_size and self.pixel_grid[row][col] != self.pixel_grid[row][col+1]:
                    x_list += [x + self.step_size/2]*2 + [np.NaN]
                    y_list += [y - self.step_size/2, y + self.step_size/2] + [np.NaN]

                # Check to add boundary on the left
                if col-1 >= 0 and self.pixel_grid[row][col] != self.pixel_grid[row][col-1]:
                    x_list += [x - self.step_size/2]*2 + [np.NaN]
                    y_list += [y - self.step_size/2, y + self.step_size/2] + [np.NaN]

                # Check to add boundary on the top
                if row+1 < y_size and self.pixel_grid[row][col] != self.pixel_grid[row+1][col]:
                    x_list += [x - self.step_size/2, x + self.step_size/2] + [np.NaN]
                    y_list += [y + self.step_size/2]*2 + [np.NaN]

                # Check to add boundary on the bottom
                if row-1 >= 0 and self.pixel_grid[row][col] != self.pixel_grid[row-1][col]:
                    x_list += [x - self.step_size/2, x + self.step_size/2] + [np.NaN]
                    y_list += [y - self.step_size/2]*2 + [np.NaN]

        # Plot the grain boundaries
        plt.plot(x_list, y_list, **settings)

def save_plot(file_path:str) -> None:
    """
    Saves the plot and clears the figure

    Parameters:
    * `file_path`: The path to save the plot
    """
    plt.savefig(file_path)
    plt.cla()
    plt.clf()
    plt.close()
