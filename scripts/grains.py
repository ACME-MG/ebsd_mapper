import sys; sys.path += [".."]
from ebsd_mapper.interface import Interface

# Initialise
itf = Interface()
itf.define_headers("x", "y", "grainId", "EulerMean_phi1", "EulerMean_Phi", "EulerMean_phi2")

# Add EBSD map used to create mesh
data_folder = "/mnt/c/Users/janzen/OneDrive - UNSW/PhD/data"
itf.import_ebsd(f"{data_folder}/2024-06-26 (ansto_617_s3)/prior_with_stage/res20gs5/ebsdExportColumnsTableReduced_FillRegion.csv", 20)
itf.import_ebsd(f"{data_folder}/2024-06-26 (ansto_617_s3)/prior_with_stage/res5gs20/ebsdExportColumnsTableReduced_FillRegion.csv", 5)

# Add EBSD maps used to create reorientation trajectories
ebsd_folder = f"{data_folder}/2024-06-26 (ansto_617_s3)/insitu_with_stage/ebsd_grains2_grainsfill_reduce"
file_path_list = [f"{ebsd_folder}/ebsd_grains2_grainsfill_reduce_{i}.csv" for i in range(1,25)]
for i, file_path in enumerate(file_path_list):
    itf.import_ebsd(file_path, 5)

# Map EBSD maps
itf.map_ebsd(
    min_area      = 1000,
    radius        = 0.2,
    tolerance     = 0.1,
    export_errors = True
)
itf.export_map()
# itf.import_map("data/grain_map.csv")

# Plot evolution of grains
for grain_id in [51, 56, 72, 80, 126, 223, 237, 262, 44, 60, 78, 86, 178, 190, 207, 244]:
    itf.plot_grain_evolution(grain_id, separate=True, white_space=False)

# # Plot EBSD maps
# itf.plot_ebsd(
#     ipf      = "x",
#     figure_x = 20,
#     grain_id = {"fontsize": 10, "color": "black"},
#     boundary = {"linewidth": 2, "color": "black"},
#     id_list  = [51, 56, 72, 80, 126, 223, 237, 262, 44, 60, 78, 86, 178, 190, 207, 244],
#     # id_list  = [59, 63, 86, 237, 303, 44, 56, 60, 141, 207, 72, 78, 126, 190, 262],
#     white_space = False,
# )
