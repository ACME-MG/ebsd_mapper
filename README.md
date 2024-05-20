# EBSD Mapper
For mapping grains across multiple EBSD maps. This repository is particularly useful for in situ EBSD where multiple EBSD maps of the same microstructure are obtained as the material specimen is deformed.

# CSV format for EBSD data

The code relies on the EBSD data to be discretised and stored in a CSV file. This CSV file must have columns for the x-coordinate, y-coordinate, grain ID, phi_1, Phi, and phi_2 values for each of the discretised cells of the EBSD map. The phi_1, Phi, and phi_2 values should be in degrees for the for the code to work properly. The following is the format for the CSV file.

|  x   |  y   | grain_id | phi_1 |  Phi  | phi_2 |
|:----:|:----:|:--------:|:-----:|:-----:|:-----:|
| 5.0  | 5.5  |    1     | 60.1  | 88.2  | 54.2  |
| 5.0  | 6.0  |    1     | 57.3  | 91.0  | 53.7  |
| 5.0  | 6.5  |    1     | 57.2  | 89.5  | 54.1  |
| 5.0  | 7.0  |    2     | 87.4  | 29.4  | 94.1  |
| 5.0  | 7.5  |    2     | 87.5  | 29.3  | 93.9  |
| ...  | ...  |   ...    |  ...  |  ...  |  ...  |

# Importing `ebsd_mapper`

The user can add the `ebsd_mapper` package to the system path so that they can import the code anywhere on their machine. This involves simply adding the following line to the `~/.bashrc` file, as follows. Note that `<path_to_ebsd_mapper>` refers to the absolute path to the `ebsd_mapper` directory.
```
export PYTHONPATH=$PYTHONPATH:<path_to_ebsd_mapper>
```

Alternatively, the user can import `ebsd_mapper` dynamically depending on the relative path between the main `ebsd_mapper` directory and their script. For instance, if the user wants to run a script in the `ebsd_mapper/scripts/` directory, they can use the following.
```
import sys; sys.path += [".."]
import ebsd_mapper
```

# Interacting with `ebsd_mapper`

The following section provides a tutorial on using the `ebsd_mapper` code.

## Interface Class

The `Interface` class allows the user to interact with the `ebsd_mapper` code. To access the `Interface` class, the user must first import the `ebsd_mapper` package and initialise an `Interface` object. The following is an example of doing so from the `ebsd_mapper/scripts/` directory.
```py
import sys; sys.path += [".."]
from ebsd_mapper import Interface
itf = Interface()
```

The `Interface` class contains several optional arguments. These include:
* `title`: This optional argument appends a title in front of the directory in which the output files will be placed in. The default value for this argument is an empty string.
* `output_path`: This optional argument defines the relative path to the output directory, which tells the script where to place the output files. The default value for this arguemnt is `"./results"`.
* `verbose`: This optional argument tells the script whether to display any information about the actions of the `Interface` class in the terminal. The default value for this argument is `True`, meaning that the information will be displayed in the terminal.
* `output_here`: This optional argument tells the script whether to just place the output files in the same directory as the script. The default value for this is `False`. Note that when the user sets the argument to `True`, the `title` and `output_path` values will not have any effect.

The implementation of the `Interface` class can be accessed via `ebsd_mapper/ebsd_mapper/itf.py`. The next sections provide descriptions of the available functions, their available arguments, and how to use them. Note that additional descriptions of the `Interface` functions can also be accessed by hovering your cursor over the functions. However, this functionality is only supported by some IDEs (e.g., Visual Studio Code).

## Defining headers of EBSD file (`define_headers`)

The `define_headers` function defines the headers for the EBSD CSV files. If the function isn't called, then default values for the headers (i.e., "x", "y", "grain_id", "phi_1", "Phi", "phi_2") will be used.

Parameters:
* `x`:        Header for the x-coordinate
* `y`:        Header for the y-coordinate
* `grain_id`: Header for the grain ID
* `phi_1`:    Header for the phi_1 values
* `Phi`:      Header for the Phi values
* `phi_2`:    Header for the phi_2 values

## Adding EBSD map and map grains (`add_ebsd`)

The `add_ebsd` function adds an EBSD map and conducts the mapping.

Parameters:
* `ebsd_path`: Path to the EBSD file as a CSV file
* `step_size`: Step size between coordinates

## Plotting the EBSD maps (`plot_ebsd`)

The `plot_ebsd` function plots the EBSD maps.

Parameters:
* `ipf`:              The IPF colour ("x", "y", "z"). The default value is "x".
* `figure_x`:         The horizontal size of the figures. The default value is 10.
* `include_id`:       Whether to include IDs in the EBSD maps; the user can define a dictionary for custom plotting settings. The default value is False.
* `include_boundary`: Whether to include IDs in the EBSD maps; the user can define a dictionary for custom plotting settings. The default value is False.
* `id_list`:          The IDs of the grains to plot the grain IDs and boundaries. The IDs should be defined based on the first grain map. If some of the defined IDs are not mappable, they will be ignored. The default value is None, which adds for all mappable grains.

## Exporting the grain mapping (`export_map`)

The `export_map` function exports the grain mapping as a CSV file. If no mapping exists, the cells of the CSV file will be empty.

# Example

The following creates a mapping between two EBSD maps, plots the EBSD maps, and exports the grain mapping.

```py
import sys; sys.path += [".."]
from ebsd_mapper.interface import Interface

itf = Interface(output_here=True)
itf.define_headers("x", "y", "grainId", "EulerMean_phi1", "EulerMean_Phi", "EulerMean_phi2")

itf.add_ebsd("ebsd_1", 0.45)
itf.add_ebsd("ebsd_2.csv", 0.60)

itf.plot_ebsd(
    ipf      = "y",
    grain_id = True,
    boundary = True,
    id_list  = [3, 6, 7, 8, 10])
itf.export_map()

```
