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
INITIAL_ANGLE = 90

#Due to the origin point on the top left, we need to invert the axis:
#INITIAL_X_POSITION_2 = TABLE_WIDTH_MM - INITIAL_X_POSITION
#INITIAL_Y_POSITION_2 = TABLE_HEIGHT_MM - INITIAL_Y_POSITION
def conversion_trigonometrique_2(angle_deg):
    angle_deg = angle_deg % 360

    if angle_deg > 180:
        angle_deg -= 360
    
    if angle_deg > 180:
        print("erreur angle > 180")
        pygame.quit()
    
    if angle_deg <= 0:
        angle_px = -180 + abs(angle_deg)
    elif angle_deg > 0:
        angle_px = 180 - angle_deg

    return angle_px

class Robot:

    def __init__(self, x= INITIAL_X_POSITION, y= INITIAL_Y_POSITION, angle=INITIAL_ANGLE, speed=4):
        self.mm_x = x
        self.mm_y = y 
        self.px_x = ((TABLE_WIDTH_MM - x) /TABLE_WIDTH_MM)*Screen_WIDTH #Due to the origin point on the top left, we need to invert the axis: 
        self.px_y = ((TABLE_HEIGHT_MM - y)/TABLE_HEIGHT_MM)*Screen_HEIGHT# valeur de x en pixel
        self.angle = angle
        self.angle_px = angle - 90
        self.angle_to_target = 0
        self.angle_diff_to_target = 0
        self.distance_x_to_target = 0
        self.distance_y_to_target = 0
        self.distance_to_target = 0
        self.speed = speed
        self.px_width = (ROBOT_WIDTH_MM/TABLE_WIDTH_MM)*Screen_WIDTH
        self.px_height = (ROBOT_HEIGHT_MM/TABLE_HEIGHT_MM)*Screen_HEIGHT
        self.mm_width = ROBOT_WIDTH_MM
        self.mm_height = ROBOT_HEIGHT_MM

    def conversion_From_mmx_To_px_x(self, mm_x):
        px_x = ((TABLE_WIDTH_MM - mm_x) /TABLE_WIDTH_MM)*Screen_WIDTH
        return px_x
    
    def conversion_From_mmy_To_px_y(self, mm_y):
        px_y = ((TABLE_HEIGHT_MM - mm_y)/TABLE_HEIGHT_MM)*Screen_HEIGHT
        return px_y

    def conversion_From_px_x_To_mm_x(self, px_x):
        x_mm = (Screen_WIDTH - px_x) * (TABLE_WIDTH_MM / Screen_WIDTH)
        return x_mm
    
    def conversion_From_px_y_To_mmy(self, px_y):
        y_mm = (Screen_HEIGHT - px_y) * (TABLE_HEIGHT_MM / Screen_HEIGHT)
        return y_mm

    def conversion_trigo_transform_rotate(self, angle):
        angle_px = (angle-90)
        return angle_px

    def calculate_target_angle(self, target_mm_x, target_mm_y):
        self.distance_x_to_target = self.mm_x - target_mm_x
        self.distance_y_to_target = target_mm_y - self.mm_y 
        self.distance_to_target = math.hypot(self.distance_x_to_target, self.distance_y_to_target)
        print(  "distance_x: ", self.distance_x_to_target, "  distance_y: ", self.distance_y_to_target)

        self.angle_to_target = int(math.degrees(math.atan2(self.distance_y_to_target, self.distance_x_to_target )))

        self.angle_diff_to_target = (self.angle_to_target - self.angle) 
        if self.angle_diff_to_target > 180:
            self.angle_diff_to_target -= 360
        print("target angle : ", self.angle_to_target)
        print("angle diff to target: ", self.angle_diff_to_target)
        return self.angle_to_target
    


    def move_towards(self, distance_to_target):
        # Convertir l'angle en radians
        radians = math.radians(self.angle)
        
        # Calculer les incréments en fonction de la vitesse
        dx = -(math.cos(radians) * self.speed)
        dy = math.sin(radians) * self.speed
        
        # Calculer la distance correspondant à un pas
        distance_step = math.hypot(dx, dy)
        
        # Vérifier si ce pas dépasse la distance restante
        if distance_step >= distance_to_target:
            # Ajuster les incréments pour atteindre exactement la cible
            ratio = distance_to_target / distance_step
            dx *= ratio
            dy *= ratio
            # Distance restante atteinte, on peut arrêter le mouvement
            distance_to_target = 0
        else:
            # Réduire la distance restante
            distance_to_target -= distance_step
            print("distance restante: ", distance_to_target)
        # Mettre à jour la position
        self.mm_x += dx
        self.mm_y += dy
        
        # Retourner la distance restante pour savoir si le robot a fini de bouger
        return distance_to_target


def conversion_From_mmx_To_px_x_2(mm_x):
    px_x = ((TABLE_WIDTH_MM - mm_x) /TABLE_WIDTH_MM)*Screen_WIDTH
    return px_x

''' 

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
        

'''