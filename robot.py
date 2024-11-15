import math
import pygame
from setup import TABLE_WIDTH_MM, TABLE_HEIGHT_MM, Screen_WIDTH, Screen_HEIGHT
# Robot specifications
ROBOT_WIDTH_MM = 320
ROBOT_HEIGHT_MM = 290
MAX_SPEED_MM_S = 200  # Max speed in mm/s
MAX_ACCEL_MM_S2 = 1000  # Max acceleration in mm/s^2
INITIAL_X_POSITION = 100
INITIAL_Y_POSITION = 100
INITIAL_ANGLE = 0

class Robot:
    def __init__(self, x=INITIAL_X_POSITION, y=INITIAL_Y_POSITION, angle=INITIAL_ANGLE, speed=0):
        self.px_x = (x /TABLE_WIDTH_MM)*Screen_WIDTH # valeur de x en pixel
        self.px_y = (y/TABLE_HEIGHT_MM)*Screen_HEIGHT
        self.mm_x = x
        self.mm_y = y 
        self.angle = angle
        self.speed = speed
        self.px_width = (ROBOT_WIDTH_MM/TABLE_WIDTH_MM)*Screen_WIDTH
        self.px_height = (ROBOT_HEIGHT_MM/TABLE_HEIGHT_MM)*Screen_HEIGHT
        self.mm_width = ROBOT_WIDTH_MM
        self.mm_height = ROBOT_HEIGHT_MM

    def calculate_target_angle(self, target_mm_x, target_mm_y):
        dx = target_mm_x - self.x
        dy = self.y - target_mm_y  # Inverted y-axis
        return math.degrees(math.atan2(dy, dx))

    def move_towards_target(self, target_x, target_y, dt):
        # Calculate distance to the target
        dx = target_x - self.x
        dy = self.y - target_y
        distance_to_target = math.hypot(dx, dy)
        
        # Calculate target angle and angle difference
        target_angle = self.calculate_target_angle(target_x, target_y)
        angle_diff = (target_angle - self.angle + 180) % 360 - 180

        # Rotate and move towards target
        if abs(angle_diff) > 1:
            self.angle += 1 * (1 if angle_diff > 0 else -1)
            self.angle %= 360
            self.speed = 0
        else:
            self.angle = target_angle
            self.speed = min(MAX_SPEED_MM_S, MAX_ACCEL_MM_S2 * distance_to_target / 50)
            self.x += self.speed * dt * math.cos(math.radians(self.angle))
            self.y -= self.speed * dt * math.sin(math.radians(self.angle))

        return distance_to_target
