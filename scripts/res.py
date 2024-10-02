import sys; sys.path += [".."]
from ebsd_mapper.interface import Interface

# Initialise
itf = Interface()
itf.define_headers("x", "y", "grainId", "EulerMean_phi1", "EulerMean_Phi", "EulerMean_phi2")

# Add EBSD map used to create mesh
data_folder = "/mnt/c/Users/z5208868/OneDrive - UNSW/PhD/data"
itf.import_ebsd(f"{data_folder}/2024-06-26 (ansto_617_s3)/prior_with_stage/res5gs20/ebsdExportColumnsTableReduced_FillRegion.csv", 5)
itf.import_ebsd(f"{data_folder}/2024-06-26 (ansto_617_s3)/prior_with_stage/res10gs10/ebsdExportColumnsTableReduced_FillRegion.csv", 10)
itf.import_ebsd(f"{data_folder}/2024-06-26 (ansto_617_s3)/prior_with_stage/res15gs10/ebsdExportColumnsTableReduced_FillRegion.csv", 15)
itf.import_ebsd(f"{data_folder}/2024-06-26 (ansto_617_s3)/prior_with_stage/res20gs5/ebsdExportColumnsTableReduced_FillRegion.csv", 20)

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
itf.plot_grain(grain_id=10)