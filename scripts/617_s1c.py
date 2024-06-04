import sys; sys.path += [".."]
from ebsd_mapper.interface import Interface

itf = Interface()
itf.define_headers("x", "y", "grainId", "EulerMean_phi1", "EulerMean_Phi", "EulerMean_phi2")
# itf.define_min_area(10000)

EBSD_FOLDER = "/mnt/c/Users/Janzen/OneDrive - UNSW/PhD/data/20240521 (ansto_617_in_situ_ebsd)"
FILE_NAME = "ebsdExportColumnsTable_fill.csv"
itf.import_ebsd(f"{EBSD_FOLDER}/14_strain_18p9pct_on_stageMapData33/{FILE_NAME}", 5)
itf.export_stats(stats_path="orientations", sort_stat="grain_id", stats=["phi_1", "Phi", "phi_2", "area"], add_header=False)
