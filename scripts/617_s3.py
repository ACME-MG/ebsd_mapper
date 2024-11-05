import sys; sys.path += [".."]
from ebsd_mapper.interface import Interface

# Initialise
itf = Interface()
itf.define_headers("x", "y", "grainId", "EulerMean_phi1", "EulerMean_Phi", "EulerMean_phi2")

# Add EBSD map used to create mesh
data_folder = "/mnt/c/Users/janzen/OneDrive - UNSW/PhD/data"
# itf.import_ebsd(f"{data_folder}/2024-06-26 (ansto_617_s3)/prior_with_stage/res10gs10/ebsdExportColumnsTableReduced_FillRegion.csv", 10)
itf.import_ebsd(f"{data_folder}/2024-06-26 (ansto_617_s3)/prior_with_stage/res20gs5/ebsdExportColumnsTableReduced_FillRegion.csv", 20)
itf.export_stats(stats_path="orientations", sort_stat="grain_id", stats=["phi_1", "Phi", "phi_2", "area"], add_header=False)

# Add EBSD maps used to create reorientation trajectories
ebsd_folder = f"{data_folder}/2024-06-26 (ansto_617_s3)/insitu_with_stage/ebsd_grains2_grainsfill_reduce"
file_path_list = [f"{ebsd_folder}/ebsd_grains2_grainsfill_reduce_{i}.csv" for i in range(1,25)]
for i, file_path in enumerate(file_path_list):
    itf.import_ebsd(file_path, 5)

# Conduct mapping
itf.map_ebsd(
    min_area      = 1000,
    radius        = 0.2,
    tolerance     = 0.1,
    export_errors = True
)
itf.export_map()
itf.plot_ebsd(
    ipf      = "x",
    figure_x = 20,
    grain_id = {"fontsize": 10, "color": "black"},
    boundary = True,
)
strain_list = [0.0, 0.0, 0.00063414, 0.00153, 0.00494, 0.0098, 0.01483, 0.02085, 0.02646, 0.03516,
               0.04409, 0.05197, 0.06013, 0.07059, 0.08208, 0.09406, 0.10561, 0.11929, 0.13656,
               0.15442, 0.18237, 0.20849, 0.23627, 0.26264, 0.28965]
itf.export_reorientation(process=True, strain_list=strain_list)

# Import map and export information
# itf.import_map("grain_map.csv")
# mapped_ids = itf.get_mapped_ids()
# itf.plot_reorientation(id_list=[269, 278, 294, 299, 302], strain_list=strain_list)
# for id in [164, 173, 265, 213, 207]:
#     itf.plot_grain(grain_id=id)
# for id in [1, 5, 6, 7, 8]:
#     itf.plot_grain(grain_id=id)
# itf.plot_reorientation(id_list=mapped_ids, strain_list=strain_list)
    
# id_grid = [mapped_ids[i:i+10] for i in range(0, len(mapped_ids), 10)]
# for id_list in id_grid:
#     itf.plot_reorientation(id_list=id_list, strain_list=strain_list)
