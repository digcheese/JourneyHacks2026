#phyphox configuration
PP_ADDRESS = "http://172.20.10.1:80"
PP_CHANNELS = ["accX","accY","accZ", "acc_time"]

import requests

import numpy as np
from scipy.integrate import cumulative_trapezoid

def accelerate_to_coords(accel_data, time_step, initial_velocity, initial_position):
    """
    Converts a 1D array of acceleration values into position coordinates.
    
    Parameters:
    accel_data (list/np.array): Acceleration values (e.g., m/s^2)
    time_step (float): Time between samples in seconds (1/frequency)
    initial_velocity (float): Starting velocity
    initial_position (float): Starting coordinate
    
    Returns:
    tuple: (velocity_array, position_array)
    """
    accel = np.array(accel_data)
    
    # 1. Integrate acceleration to get velocity
    # initial value ensures the output array is the same length as input
    velocity = cumulative_trapezoid(accel, dx=time_step, initial=initial_velocity)
    
    # 2. Integrate velocity to get position (coordinates)
    position = cumulative_trapezoid(velocity, dx=time_step, initial=initial_position)
    
    return velocity, position

def d_coords(accel_data, last_accel, last_vel):
    d_point = [0,0,0]
    vel = last_vel
    
    vel[0], d_point[0] = accelerate_to_coords(accel_data[0], accel_data[3]-last_accel[3], vel[0], d_point[0])
    vel[1], d_point[1] = accelerate_to_coords(accel_data[1], accel_data[3]-last_accel[3], vel[1], d_point[1])
    vel[2], d_point[2] = accelerate_to_coords(accel_data[2], accel_data[3]-last_accel[3], vel[2], d_point[2])

    return d_point[0:2], vel
    
def next_point(points, vels, accels, prev_accels):
    next_point = points[-1]

    change, next_vel = d_coords(accels, prev_accels, vels[-1])
    for i in range(0,2):
        next_point[i] += change[i]
    

    vels.append(next_vel)
    points.append(next_point)
    return



accels = [0,0,0,0]
prev_accels = [0,0,0,0]

prev_vel = 0
list_of_points = [[0,0]]

while True:
    url = PP_ADDRESS + "/get?" + ("&".join(PP_CHANNELS))
    data = requests.get(url=url).json()

    accX = data["buffer"]['accX']['buffer'][0]
    accY = data["buffer"]['accY']['buffer'][0]
    accZ = data["buffer"]['accZ']['buffer'][0]
    acc_time = data["buffer"]['acc_time']['buffer'][0]
    
    
    accels = [accX, accY, accZ, acc_time]
    
    next_point(list_of_points, prev_vel, accels, prev_accels)
    
    prev_accels = accels



