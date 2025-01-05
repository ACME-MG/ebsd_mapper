"""
 Title:         Grains
 Description:   For manually plotting grains
 Author:        Janzen Choi

"""

# Libraries
import sys; sys.path += [".."]
from ebsd_mapper.interface import Interface

# Constants
DATA_FOLDER = "/mnt/c/Users/janzen/OneDrive - UNSW/PhD/data"
INIT_PATH = f"{DATA_FOLDER}/2024-06-26 (ansto_617_s3)/prior_with_stage/res5gs20/ebsdExportColumnsTableReduced_FillRegion.csv"
EBSD_FOLDER = f"{DATA_FOLDER}/2024-06-26 (ansto_617_s3)/insitu_with_stage/ebsd_grains2_grainsfill_reduce"
CAL_GRAIN_IDS = [59, 63, 86, 237, 303]
VAL_GRAIN_IDS = [44, 53, 60, 78, 190]

# Initialise
itf = Interface()
itf.define_headers("x", "y", "grainId", "EulerMean_phi1", "EulerMean_Phi", "EulerMean_phi2")

# Plot grain 59
# x_ticks = [0+i for i in [0, 300, 600, 900, 1200, 1500]]
# y_ticks = [350+i for i in [0, 150, 300, 450]]
# itf.import_ebsd(INIT_PATH, 5)
# itf.plot_grains_manual([157, 170], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{10}.csv", 5)
# itf.plot_grains_manual([190, 211], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{19}.csv", 5)
# itf.plot_grains_manual([195, 219], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{24}.csv", 5)
# itf.plot_grains_manual([225], x_ticks, y_ticks)

# # Plot grain 63
# x_ticks = [50+i for i in [0, 300, 600, 900, 1200, 1500]]
# y_ticks = [300+i for i in [0, 150, 300, 450]]
# itf.import_ebsd(INIT_PATH, 5)
# itf.plot_grains_manual([177], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{10}.csv", 5)
# itf.plot_grains_manual([215], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{19}.csv", 5)
# itf.plot_grains_manual([229], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{24}.csv", 5)
# itf.plot_grains_manual([228], x_ticks, y_ticks)

# # Plot grain 86
# x_ticks = [150+i for i in [0, 300, 600, 900, 1200, 1500]]
# y_ticks = [550+i for i in [0, 150, 300, 450]]
# itf.import_ebsd(INIT_PATH, 5)
# itf.plot_grains_manual([239], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{10}.csv", 5)
# itf.plot_grains_manual([249, 279], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{19}.csv", 5)
# itf.plot_grains_manual([228, 255, 280], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{24}.csv", 5)
# itf.plot_grains_manual([232, 250, 266], x_ticks, y_ticks)

# # Plot grain 237
# x_ticks = [1450+i for i in [0, 300, 600, 900, 1200, 1500]]
# y_ticks = [1100+i for i in [0, 150, 300, 450]]
# itf.import_ebsd(INIT_PATH, 5)
# itf.plot_grains_manual([576, 579, 584, 585, 574, 563], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{10}.csv", 5)
# itf.plot_grains_manual([616, 621, 624, 625, 613], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{19}.csv", 5)
# itf.plot_grains_manual([550, 574, 581, 579], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{23}.csv", 5) # not 24 (merges)
# itf.plot_grains_manual([502, 511], x_ticks, y_ticks)

# # Plot grain 303
# x_ticks = [1900+i for i in [0, 300, 600, 900, 1200, 1500]]
# y_ticks = [700+i for i in [0, 150, 300, 450]]
# itf.import_ebsd(INIT_PATH, 5)
# itf.plot_grains_manual([741], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{10}.csv", 5)
# itf.plot_grains_manual([785], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{19}.csv", 5)
# itf.plot_grains_manual([724], x_ticks, y_ticks)
# itf.import_ebsd(f"{EBSD_FOLDER}/ebsd_grains2_grainsfill_reduce_{24}.csv", 5)
# itf.plot_grains_manual([627], x_ticks, y_ticks)

# Plot EBSD map for verification
# itf.plot_ebsd(
#     ipf      = "x",
#     figure_x = 20,
#     grain_id = {"fontsize": 10, "color": "black"},
#     boundary = True,
# )
