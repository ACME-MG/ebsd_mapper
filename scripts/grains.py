import sys; sys.path += [".."]
from ebsd_mapper.interface import Interface

# Constants
# GRAIN_IDS = [60, 79, 178, 189, 190, 215, 237, 278, 14, 56, 72, 101, 223, 255, 262, 299]
# GRAIN_IDS = [95, 136, 141, 179, 207, 240, 262, 287, 14, 50, 101, 122, 138, 164, 223, 306]
GRAIN_IDS = [14, 72, 95, 101, 207, 240, 262, 287, 39, 50, 138, 164, 185, 223, 243, 238]

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
# itf.map_ebsd(
#     min_area      = 1000,
#     radius        = 0.2,
#     tolerance     = 0.1,
#     export_errors = True
# )
# itf.export_map()
itf.import_map("data/grain_map.csv")

# Plot EBSD maps
itf.plot_ebsd(
    ipf      = "x",
    figure_x = 20,
    # grain_id = {"fontsize": 10, "color": "black"},
    boundary = {"linewidth": 2, "color": "black"},
    id_list = GRAIN_IDS,
    white_space = False,
)

# strain_list = [0.0, 0.0, 0.0, 0.00063414, 0.00153, 0.00494, 0.0098, 0.01483, 0.02085, 0.02646, 0.03516,
#                0.04409, 0.05197, 0.06013, 0.07059, 0.08208, 0.09406, 0.10561, 0.11929, 0.13656,
#                0.15442, 0.18237, 0.20849, 0.23627, 0.26264, 0.28965]
# itf.export_reorientation(process=True, strain_list=strain_list)

# Plot evolution of grains
for grain_id in GRAIN_IDS:
    itf.plot_grain_evolution(grain_id, separate=True, white_space=False)
