import math
import pygame
from setup import TABLE_WIDTH_MM, TABLE_HEIGHT_MM, Screen_WIDTH, Screen_HEIGHT
# Robot specifications
ROBOT_WIDTH_MM = 320
ROBOT_HEIGHT_MM = 290
MAX_SPEED_MM_S = 200  # Max speed in mm/s
MAX_ACCEL_MM_S2 = 1000  # Max acceleration in mm/s^2
INITIAL_X_POSITION = 400
INITIAL_Y_POSITION = 500
INITIAL_ANGLE = 0

#Due to the origin point on the top left, we need to invert the axis:
#INITIAL_X_POSITION_2 = TABLE_WIDTH_MM - INITIAL_X_POSITION
#INITIAL_Y_POSITION_2 = TABLE_HEIGHT_MM - INITIAL_Y_POSITION

class Robot:
    def __init__(self, x= INITIAL_X_POSITION, y= INITIAL_Y_POSITION, angle=INITIAL_ANGLE, speed=0):
        self.mm_x = x
        self.mm_y = y 
        self.px_x = ((TABLE_WIDTH_MM - x) /TABLE_WIDTH_MM)*Screen_WIDTH #Due to the origin point on the top left, we need to invert the axis: 
        self.px_y = ((TABLE_HEIGHT_MM - y)/TABLE_HEIGHT_MM)*Screen_HEIGHT# valeur de x en pixel
        self.angle = angle
        self.speed = speed
        self.px_width = (ROBOT_WIDTH_MM/TABLE_WIDTH_MM)*Screen_WIDTH
        self.px_height = (ROBOT_HEIGHT_MM/TABLE_HEIGHT_MM)*Screen_HEIGHT
        self.mm_width = ROBOT_WIDTH_MM
        self.mm_height = ROBOT_HEIGHT_MM

    def calculate_target_angle_relatif_absolu_distance(self, target_mm_x, target_mm_y):
        print("Début du go_to")

        # Initialisation des variables
        rotation_to_do_relatif = 0
        angle_objectif_absolue = 0

        # Calcul des distances en x et y
        to_do_x = self.mm_x - target_mm_x
        to_do_y = self.mm_y - target_mm_y

        print(f"to do_y: {to_do_y}  to do_x: {to_do_x}")

        # Calcul de la distance et de l'angle en degrés
        distance = math.sqrt(to_do_x ** 2 + to_do_y ** 2)
        teta_calcule = abs(math.degrees(math.atan(abs(to_do_y) / abs(to_do_x))))

        # Calcul de l'angle objectif en fonction du quadrant
        if to_do_y > 0 and to_do_x > 0:
            angle_objectif_absolue = 90 + teta_calcule
            print(" (90 + teta_calcule) ")
        elif to_do_y < 0 and to_do_x > 0:
            angle_objectif_absolue = 90 - teta_calcule
            print(" (90 - teta_calcule) ")
        elif to_do_y > 0 and to_do_x < 0:
            angle_objectif_absolue = 270 - teta_calcule
            print(" (270 - teta_calcule) ")
        elif to_do_y < 0 and to_do_x < 0:
            angle_objectif_absolue = 270 + teta_calcule
            print(" (270 + teta_calcule) ")

        print(f"teta_objectif: {angle_objectif_absolue}")

        # Calcul de l'angle de rotation nécessaire
        rotation_to_do_relatif = angle_objectif_absolue - self.angle

        if rotation_to_do_relatif >= 180:
            rotation_to_do_relatif = rotation_to_do_relatif - 360
        elif rotation_to_do_relatif < -180:
            rotation_to_do_relatif = rotation_to_do_relatif + 360

        #print(f"teta_goal: {teta_goal}")
        print("initial_x:",self.mm_x,"  initial_y:",self.mm_y,"  teta_goal :",rotation_to_do_relatif)
        return rotation_to_do_relatif, angle_objectif_absolue, distance
        
    def move_towards_target(self, target_mm_x, target_mm_y, dt):
        # Calculate distance to the target
        dx = target_mm_x - self.x
        dy = self.y - target_mm_y
        distance_to_target = math.hypot(dx, dy)
        
        # Calculate target angle and angle difference
        target_angle = self.calculate_target_angle(target_mm_x, target_mm_y)
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
