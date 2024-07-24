import sys; sys.path += [".."]
from ebsd_mapper.interface import Interface

# Initialise
itf = Interface()
itf.define_headers("x", "y", "grainId", "EulerMean_phi1", "EulerMean_Phi", "EulerMean_phi2")
itf.define_min_area(5000)

# Add EBSD map used to create mesh
data_folder = "/mnt/c/Users/Janzen/OneDrive - UNSW/PhD/data"
itf.import_ebsd(f"{data_folder}/2024-06-26 (ansto_617_s3)/prior_with_stage/res20gs5/ebsdExportColumnsTableReduced_FillRegion.csv", 20)
itf.export_stats(stats_path="orientations", sort_stat="grain_id", stats=["phi_1", "Phi", "phi_2", "area"], add_header=False)

# Add EBSD maps used to create reorientation trajectories
ebsd_folder = f"{data_folder}/2024-06-26 (ansto_617_s3)/insitu_with_stage/ebsd_grains2_grainsfill_reduce"
file_path_list = [f"{ebsd_folder}/ebsd_grains2_grainsfill_reduce_{i}.csv" for i in range(1,25)]
for i, file_path in enumerate(file_path_list):
    itf.import_ebsd(file_path, 5)

# # Conduct mapping
# itf.map_ebsd()
# itf.export_map()
# itf.plot_ebsd(
#     ipf      = "x",
#     figure_x = 20,
#     grain_id = {"fontsize": 10, "color": "black"},
#     boundary = True,
# )
# itf.export_reorientation()

# Import map and export information 
itf.import_map("results/240714181646_617_s3/grain_map.csv")
# itf.export_stats()
id_list = itf.__controller__.map_dict["ebsd_1"]
for id in id_list:
    itf.plot_grain(grain_id=id)
    itf.plot_reorientation(plot_path=f"reorientation_{id}", id_list=[id])
