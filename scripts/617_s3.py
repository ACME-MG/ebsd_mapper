import sys; sys.path += [".."]
from ebsd_mapper.interface import Interface

itf = Interface()

itf.define_headers("x", "y", "grainId", "EulerMean_phi1", "EulerMean_Phi", "EulerMean_phi2")
itf.define_min_area(5000)

EBSD_FOLDER = "/mnt/c/Users/Janzen/OneDrive - UNSW/PhD/data/2024-06-26 (ansto_617_s3)/insitu_with_stage/ebsd_grains2_grainsfill_reduce"
FILE_NAME_LIST = [f"ebsd_grains2_grainsfill_reduce_{i}.csv" for i in range(1,25)]
for i, file_name in enumerate(FILE_NAME_LIST):
    file_path = f"{EBSD_FOLDER}/{file_name}"
    itf.import_ebsd(file_path, 5)
    if i == 0:
        itf.export_stats(stats_path="orientations", sort_stat="grain_id", stats=["phi_1", "Phi", "phi_2", "area"], add_header=False)

# itf.map_ebsd()
# itf.export_map()
# itf.export_stats()
# itf.plot_ebsd(
#     ipf      = "x",
#     figure_x = 20,
#     grain_id = {"fontsize": 10, "color": "black"},
#     boundary = True,
# )

itf.import_map("results/240629170626_617_s3/grain_map.csv")
itf.export_reorientation()

id_list = [17, 22, 27, 37, 44]
for id in id_list:
    itf.plot_reorientation(id_list=[id])
    itf.plot_grain(grain_id=id)

# cal_id_list = [56, 346, 463, 568, 650] # [75, 189, 314, 346, 463]
# val_id_list = [35, 96, 117, 123, 135, 215, 346, 462, 463, 593, 650, 696, 745]
# itf.plot_reorientation(id_list=cal_id_list)
# for id in cal_id_list:
#     itf.plot_grain(grain_id=id)
