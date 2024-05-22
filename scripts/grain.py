import sys; sys.path += [".."]
from ebsd_mapper.interface import Interface

itf = Interface("p91", output_here=True)
itf.define_headers("x", "y", "grainId", "EulerMean_phi1", "EulerMean_Phi", "EulerMean_phi2")

EBSD_FOLDER = "/mnt/c/Users/Janzen/OneDrive - UNSW/PhD/data/20240516 (ondrej_P91)"
itf.import_ebsd(f"{EBSD_FOLDER}/S1_2/deer-in/res_015um/ebsdExportColumnsTable_fill.csv", 0.15)
itf.import_ebsd(f"{EBSD_FOLDER}/S1_2/deer-in/res_030um/ebsdExportColumnsTable_fill.csv", 0.30)
itf.import_ebsd(f"{EBSD_FOLDER}/S1_2/deer-in/res_045um/ebsdExportColumnsTable_fill.csv", 0.45)
itf.import_ebsd(f"{EBSD_FOLDER}/S1_2/deer-in/res_060um/ebsdExportColumnsTable_fill.csv", 0.60)
itf.map_ebsd()
itf.export_map()
# itf.import_map("grain_map.csv")

# itf.plot_ebsd(
#     ipf      = "x",
#     grain_id = True,
#     boundary = True,
# )
itf.plot_grain(9)
