import numpy as np
from scipy.spatial.transform import Rotation as R
from scipy.interpolate import splprep, splev
import matplotlib.pyplot as plt

# Sample Euler angles in degrees (phi1, Phi, phi2)
euler_angles = np.array([
    [30, 45, 60],
    [35, 50, 65],
    [40, 55, 70],
    [45, 60, 75],
    [50, 65, 80]
])

# Convert Euler angles to rotation matrices
rotations = R.from_euler('zxz', euler_angles, degrees=True)

# Convert rotation matrices to quaternions
quaternions = rotations.as_quat()

# Fit a spline to the quaternion data
tck, u = splprep(quaternions.T, s=0, k=3)

# Evaluate the spline to get the points and their derivatives
t = np.linspace(0, 1, num=100)
spline_points = np.array(splev(t, tck))
spline_derivative_1 = np.array(splev(t, tck, der=1))
spline_derivative_2 = np.array(splev(t, tck, der=2))

# Calculate the curvature of the spline
numerator = np.linalg.norm(np.cross(spline_derivative_1.T, spline_derivative_2.T), axis=1)
denominator = np.linalg.norm(spline_derivative_1.T, axis=1) ** 3
curvature = numerator / denominator

# Plot the curvature
plt.plot(t, curvature)
plt.xlabel('Parameter t')
plt.ylabel('Curvature')
plt.title('Curvature of the Best Fit Spline')
plt.show()