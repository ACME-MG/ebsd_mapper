import sys; sys.path += [".."]
from ebsd_mapper.mapper.reorientation import process_trajectory
from ebsd_mapper.plotting.pole_figure import IPF, get_lattice
from ebsd_mapper.helper.general import transpose
from ebsd_mapper.helper.io import csv_to_dict
from ebsd_mapper.helper.plotter import save_plot
from ebsd_mapper.maths.orientation import euler_to_quat, quat_to_euler
import math, numpy as np

def slerp(quat_1, quat_2, t=0.5):
    quat_1 = np.array(quat_1)
    quat_2 = np.array(quat_2)
    theta = math.acos(np.dot(quat_1, quat_2))
    if abs(math.sin(theta)) < 1e-6:
        return quat_1
    factor_1 = math.sin((1-t)*theta)/math.sin(theta)
    factor_2 = math.sin(t*theta)/math.sin(theta)
    quat_12 = factor_1*quat_1 + factor_2*quat_2
    return list(quat_12 / np.linalg.norm(quat_12))

def slerp_trajectory(euler_list):
    quat_list = [euler_to_quat(euler) for euler in euler_list]
    new_quat_list = [quat_list[0]]
    for curr_quat in quat_list[1:-1]:
        prev_quat = new_quat_list[-1]
        new_quat = slerp(prev_quat, curr_quat, 0.5)
        new_quat_list.append(new_quat)
    new_euler_list = [quat_to_euler(new_quat) for new_quat in new_quat_list]
    new_euler_list += [euler_list[-1]]
    return new_euler_list

def smooth_trajectory(euler_list:list, degree:int=3) -> list:
    quat_list  = [euler_to_quat(euler) for euler in euler_list]
    trans_list = transpose(quat_list)
    x_list     = list(range(len(quat_list)))
    poly_list  = [np.polyfit(x_list, q, degree) for q in trans_list]
    eval_list  = [np.polyval(poly, x_list) for poly in poly_list]
    quat_list  = transpose(eval_list)
    euler_list = [quat_to_euler(quat) for quat in quat_list]
    return euler_list

trajectory = [
    [1.524204239, 1.837390658, 4.174846246],
    [1.523771223, 1.837040894, 4.174476236],
    [1.532707308, 1.835679537, 4.208028096],
    [1.522870982, 1.836859903, 4.154025864],
    [3.254464842, 2.092478207, 3.448336888],
    [3.266187346, 2.16214477, 3.463201857],
    [3.264449347, 2.141984297, 3.460044731],
    [3.268028493, 2.152271093, 3.464680151],
    [3.282127089, 2.215111847, 3.48482317],
    [3.266162736, 2.106727599, 3.462896948],
    [3.264264691, 2.071809669, 5.030914361],
    [3.297195912, 2.242734301, 5.076852475],
    [3.281363507, 2.143564518, 5.052213138],
    [3.280184712, 2.123663401, 5.05025802],
    [5.750454271, 2.606579599, 0.984443889],
    [5.808160266, 2.540685391, 5.753863073],
    [5.82298614, 2.515359791, 5.770259744],
    [3.299415797, 2.142378043, 3.494070623],
    [3.300658471, 2.122911863, 3.491676031],
    [3.299989137, 2.097497425, 5.060539755],
    [5.822742667, 2.513982727, 4.185407059],
    [5.822763785, 2.508058206, 5.74561936],
    [1.578640884, 1.881872643, 2.624259435],
    [1.575983969, 1.888975434, 4.176648647],
    [1.580597921, 1.895398246, 4.177315363],
]


strain_list = [0.0, 0.0, 0.00063414, 0.00153, 0.00494, 0.0098, 0.01483, 0.02085, 0.02646, 0.03516,
               0.04409, 0.05197, 0.06013, 0.07059, 0.08208, 0.09406, 0.10561, 0.11929, 0.13656,
               0.15442, 0.18237, 0.20849, 0.23627, 0.26264, 0.28965]
new_trajectory = process_trajectory(trajectory, strain_list)

print(len(strain_list))
print(len(trajectory))
print(len(new_trajectory))

ipf = IPF(get_lattice("fcc"))
direction = [1,0,0]

ipf.plot_ipf_trajectory([trajectory], direction, "plot", {"color": "darkgray", "linewidth": 2})
ipf.plot_ipf_trajectory([trajectory], direction, "arrow", {"color": "darkgray", "head_width": 0.01, "head_length": 0.015})

ipf.plot_ipf_trajectory([new_trajectory], direction, "plot", {"color": "green", "linewidth": 1, "zorder": 3})
ipf.plot_ipf_trajectory([new_trajectory], direction, "arrow", {"color": "green", "head_width": 0.0075, "head_length": 0.0075*1.5, "zorder": 3})

save_plot("temp.png")

# Try fitting the phi angles using polynomials
# Increase bounds by pi on each side?

