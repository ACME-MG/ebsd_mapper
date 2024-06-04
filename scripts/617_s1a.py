import sys; sys.path += [".."]
from ebsd_mapper.interface import Interface

itf = Interface()
itf.define_headers("x", "y", "grainId", "EulerMean_phi1", "EulerMean_Phi", "EulerMean_phi2")
itf.define_min_area(10000)

EBSD_FOLDER = "/mnt/c/Users/Janzen/OneDrive - UNSW/PhD/data/20240521 (ansto_617_in_situ_ebsd)"
FILE_NAME = "ebsdExportColumnsTable_fill.csv"
itf.import_ebsd(f"{EBSD_FOLDER}/01_strain_0pct_on_stage_finalMapData20/{FILE_NAME}", 5)
itf.export_stats(stats_path="orientations", sort_stat="grain_id", stats=["phi_1", "Phi", "phi_2", "area"], add_header=False)
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

id_list = []
itf.import_map("results/240522165157_617/grain_map.csv")
itf.export_reorientation()
itf.plot_reorientation(id_list=id_list)
