#phyphox configuration
PP_ADDRESS = "http://172.20.10.1:80"
PP_CHANNELS = ["lin_accX","lin_accY","lin_accZ", "lin_acc_time"]

import requests

import numpy as np
from scipy.integrate import cumulative_trapezoid

class RealTimePositionTracker:
    def __init__(self, accel_threshold=0.01):
        # State variables
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.position = np.array([0.0, 0.0, 0.0])
        self.last_accel = np.array([0.0, 0.0, 0.0])
        self.last_time = None
                
        # Filtering
        self.accel_threshold = accel_threshold # Meters/s^2
        self.friction = 0.95
        
        self.stationary_counter = 0
        self.stationary_threshold = 10

    def update(self, accel_input, current_time):
        """
        accel_input: list or np.array [x, y, z] in m/s^2
        current_time: timestamp in seconds
        Returns: current position [x, y, z]
        """

        # 1. Initialize time on first run
        if self.last_time is None:
            self.last_time = current_time
            return self.position
        
        # 2. Calculate time delta (dt)
        dt = current_time - self.last_time
        if dt <= 0: return self.position # Handle duplicate timestamps

        # 3. Thresholding Noise
        
        acc_magnitude = np.linalg.norm(accel_input)
        if acc_magnitude < self.accel_threshold:
            # If acceleration is tiny, treat it as 0
            accel_input = np.array([0.0, 0.0, 0.0])
            self.stationary_counter += 1
        else:
            self.stationary_counter = 0

        # If we have been stationary for a while, force velocity to 0 (Stops drift!)
        if self.stationary_counter > self.stationary_threshold:
            self.velocity = np.array([0.0, 0.0, 0.0])   
                
                        
        accel_linear = np.array(accel_input)


        # 4. Trapezoidal Integration for Velocity
        # v = v0 + 0.5 * (a0 + a1) * dt
        new_velocity = self.velocity + 0.5 * (self.last_accel + accel_linear) * dt * self.friction

        # 5. Trapezoidal Integration for Position
        # p = p0 + 0.5 * (v0 + v1) * dt
        new_position = self.position + 0.5 * (self.velocity + new_velocity) * dt

        # 6. Update State
        self.velocity = new_velocity
        self.position = new_position
        self.last_accel = accel_linear
        self.last_time = current_time

        return self.position




tracker = RealTimePositionTracker(accel_threshold=0.2)


while True:
    url = PP_ADDRESS + "/get?" + ("&".join(PP_CHANNELS))
    data = requests.get(url=url).json()

    accX = data["buffer"]["" + PP_CHANNELS[0]]['buffer'][0]
    accY = data["buffer"]["" + PP_CHANNELS[1]]['buffer'][0]
    accZ = data["buffer"]["" + PP_CHANNELS[2]]['buffer'][0]
    acc_time = data["buffer"]["" + PP_CHANNELS[3]]['buffer'][0]


    accels = [accX, accY, accZ]
    
    pos = tracker.update(accels, acc_time)
    print(pos)



