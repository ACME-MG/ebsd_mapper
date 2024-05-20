import sys; sys.path += [".."]
from ebsd_mapper.interface import Interface

itf = Interface(output_here=True)
itf.define_headers("x", "y", "grainId", "EulerMean_phi1", "EulerMean_Phi", "EulerMean_phi2")

EBSD_FOLDER = "/mnt/c/Users/Janzen/OneDrive - UNSW/PhD/data/20240516 (ondrej_P91)"
# itf.add_ebsd(f"{EBSD_FOLDER}/S1_2/deer-in/res_015um/ebsdExportColumnsTableJanzen_fill.csv", 0.15)
# itf.add_ebsd(f"{EBSD_FOLDER}/S1_2/deer-in/res_030um/ebsdExportColumnsTableJanzen_fill.csv", 0.30)
itf.add_ebsd(f"{EBSD_FOLDER}/S1_2/deer-in/res_045um/ebsdExportColumnsTableJanzen_fill.csv", 0.45)
itf.add_ebsd(f"{EBSD_FOLDER}/S1_2/deer-in/res_060um/ebsdExportColumnsTableJanzen_fill.csv", 0.60)

id_list = [3, 6, 7, 8, 10]
itf.plot_ebsd(include_id=True, include_boundary=True, id_list=id_list)
itf.export_map()
