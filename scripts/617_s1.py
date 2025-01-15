import sys; sys.path += [".."]
from ebsd_mapper.interface import Interface

itf = Interface()

itf.define_headers("x", "y", "grainId", "EulerMean_phi1", "EulerMean_Phi", "EulerMean_phi2")

EBSD_FOLDER = "/mnt/c/Users/Janzen/OneDrive - UNSW/PhD/data/2024-05-23 (ansto_617_s1)/hagb15/"
FILE_NAME = "ebsdExportColumnsTable_NoFill.csv"

itf.import_ebsd(f"{EBSD_FOLDER}/01_strain_0pct_on_stage_finalMapData20/{FILE_NAME}", 5)
# itf.export_stats(stats_path="orientations", sort_stat="grain_id", stats=["phi_1", "Phi", "phi_2", "area"], add_header=False)
# itf.export_stats(stats_path="stats", sort_stat="area", descending=True, stats=["grain_id", "phi_1", "Phi", "phi_2", "area"], add_header=True)
itf.import_ebsd(f"{EBSD_FOLDER}/02_strain_0p3pct_on_stageMapData21/{FILE_NAME}", 5)
itf.import_ebsd(f"{EBSD_FOLDER}/03_strain_0p8pct_on_stageMapData22/{FILE_NAME}", 5)
itf.import_ebsd(f"{EBSD_FOLDER}/04_strain_2p2pct_on_stageMapData23/{FILE_NAME}", 5)
itf.import_ebsd(f"{EBSD_FOLDER}/05_strain_3p3pct_on_stageMapData24/{FILE_NAME}", 5)
itf.import_ebsd(f"{EBSD_FOLDER}/06_strain_3p6pct_on_stageMapData25/{FILE_NAME}", 5)
itf.import_ebsd(f"{EBSD_FOLDER}/07_strain_4p8pct_on_stageMapData26/{FILE_NAME}", 5)
itf.import_ebsd(f"{EBSD_FOLDER}/08_strain_7p5pct_on_stageMapData27/{FILE_NAME}", 5)
itf.import_ebsd(f"{EBSD_FOLDER}/09_strain_9p4pct_on_stageMapData28/{FILE_NAME}", 5)
itf.import_ebsd(f"{EBSD_FOLDER}/10_strain_11pct_on_stageMapData29/{FILE_NAME}", 5)
itf.import_ebsd(f"{EBSD_FOLDER}/11_strain_13p2pct_on_stageMapData30/{FILE_NAME}", 5)
itf.import_ebsd(f"{EBSD_FOLDER}/12_strain_14p4pct_on_stageMapData31/{FILE_NAME}", 5)
itf.import_ebsd(f"{EBSD_FOLDER}/13_strain_16p5pct_on_stageMapData32/{FILE_NAME}", 5)
itf.import_ebsd(f"{EBSD_FOLDER}/14_strain_18p9pct_on_stageMapData33/{FILE_NAME}", 5)

# itf.map_ebsd()
# itf.export_map()
# itf.export_stats()
# itf.plot_ebsd(
#     ipf      = "x",
#     figure_x = 20,
#     grain_id = {"fontsize": 10, "color": "black"},
#     boundary = True,
# )

itf.import_map("results/240523154426_617_s1b/grain_map.csv")
# itf.export_reorientation()

cal_id_list = [56, 346, 463, 568, 650] # [75, 189, 314, 346, 463]
# val_id_list = [35, 96, 117, 123, 135, 215, 346, 462, 463, 593, 650, 696, 745]
itf.plot_reorientation(id_list=cal_id_list)
for id in cal_id_list:
    itf.plot_grain_evolution(grain_id=id)