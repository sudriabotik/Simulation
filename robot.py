import math
import pygame
from setup import TABLE_WIDTH_MM, TABLE_HEIGHT_MM, Screen_WIDTH, Screen_HEIGHT
# Robot specifications
ROBOT_WIDTH_MM = 320
ROBOT_HEIGHT_MM = 290
INITIAL_X_POSITION = 300
INITIAL_Y_POSITION = 950
INITIAL_ANGLE = 0

MAX_SPEED_MM_S = 400*2  # Vitesse maximale en mm/s
MAX_ACCEL_MM_S2 = 600*2  # Accélération maximale en mm/s^2
MAX_TURNING_SPEED = 90*2  # Vitesse de rotation en degrés par seconde

ROTATION_THRESHOLD = 1
DISTANCE_THRESHOLD = 1

FPS = 30

class Graphique:
    def __init__(self, robot, image_robot, screen, scaled_vinyle):
        self.robot = robot  # Référence à l'instance de Robot existante
        self.image_robot = image_robot
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.scaled_vinyle = scaled_vinyle

    def refesh_graphique(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.scaled_vinyle, (0, 0))
        self.robot.angle_px =self.robot.conversion_trigo_transform_rotate(self.robot.angle) 
        self.robot.px_x = self.robot.conversion_From_mmx_To_px_x(self.robot.mm_x)
        self.robot.px_y = self.robot.conversion_From_mmy_To_px_y(self.robot.mm_y)

        rotated_image = pygame.transform.rotate(self.image_robot, self.robot.angle_px)
        robot_rect = rotated_image.get_rect(center=(self.robot.px_x, self.robot.px_y))
        self.screen.blit(rotated_image, robot_rect)

        coords_text = self.font.render(f"X: {int(self.robot.mm_x)} mm, Y: {int(self.robot.mm_y)} mm, O: {int(self.robot.angle)}", True, (255, 255, 255))
        self.screen.blit(coords_text, (10, 10))  # Position du texte en haut à gauche

        pygame.display.update()

class Robot(Graphique):
    clock = pygame.time.Clock()
    def __init__(self,scaled_vinyle=None, screen=None, image_robot= None, x= INITIAL_X_POSITION, y= INITIAL_Y_POSITION, angle=INITIAL_ANGLE, speed=0):
        self.mm_x = x
        self.mm_y = y 
        self.px_x = ((TABLE_WIDTH_MM - x) /TABLE_WIDTH_MM)*Screen_WIDTH #Due to the origin point on the top left, we need to invert the axis: 
        self.px_y = ((TABLE_HEIGHT_MM - y)/TABLE_HEIGHT_MM)*Screen_HEIGHT# valeur de x en pixel
        self.angle = angle
        self.angle_px = angle - 90
        self.angle_to_target = angle
        self.angle_diff_to_target = 0
        self.distance_x_to_target = 0
        self.distance_y_to_target = 0
        self.distance_to_target = 0
        self.speed = speed  # Vitesse actuelle en mm/s
        self.acceleration = MAX_ACCEL_MM_S2
        self.turning_speed = MAX_TURNING_SPEED  # En degrés par seconde
        self.target_speed = MAX_SPEED_MM_S  # Vitesse cible

        self.px_width = (ROBOT_WIDTH_MM/TABLE_WIDTH_MM)*Screen_WIDTH
        self.px_height = (ROBOT_HEIGHT_MM/TABLE_HEIGHT_MM)*Screen_HEIGHT
        self.mm_width = ROBOT_WIDTH_MM
        self.mm_height = ROBOT_HEIGHT_MM

        if image_robot and screen and scaled_vinyle:
            self.graphique = Graphique(self, image_robot, screen, scaled_vinyle)
        else:
            self.graphique = None  # Si l'image ou l'écran manque, pas de rendu graphique
            print("erreur, missing arg: image ou screen")


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
    
    def normalize_angle(self, angle):
        angle = angle % 360  
        if angle > 180:
            angle -= 360  
        return angle

    def update_target_speed(self, distance):
        # Calculate the deceleration distance based on the robot's max speed and acceleration
        deceleration_distance = (MAX_SPEED_MM_S ** 2) / (2 * MAX_ACCEL_MM_S2)

        if distance < deceleration_distance:
            # Reduce speed proportionally to the remaining distance
            self.target_speed = max(0, (distance / deceleration_distance) * MAX_SPEED_MM_S)
        else:
            # Maintain maximum speed
            self.target_speed = MAX_SPEED_MM_S


    def update_speed(self, dt, distance_restante):
        #distance_restante = abs(distance_restante) # pour gérer les valeur négative
        self.update_target_speed(distance_restante)  # Met à jour la vitesse cible en fonction de la distance
        if self.speed < self.target_speed:
            self.speed = min(self.speed + self.acceleration * dt, self.target_speed)
            print("update_augmentation_speed: ", self.speed)
        elif self.speed > self.target_speed:
            self.speed = max(self.speed - self.acceleration * dt, self.target_speed)
            print("update_diminution_speed: ", self.speed)

    def update_turning_speed(self, dt, angle_diff_restante):
    # Calcul de l'accélération angulaire
        max_deceleration_angle = (MAX_TURNING_SPEED ** 2) / (2 * self.acceleration)

        # Si proche de l'objectif, décélérer
        if abs(angle_diff_restante) < max_deceleration_angle:
            self.turning_speed = max(0, (abs(angle_diff_restante) / max_deceleration_angle) * MAX_TURNING_SPEED)
        else:
            # Sinon, utiliser la vitesse angulaire maximale
            self.turning_speed = MAX_TURNING_SPEED

        # Ajuster la vitesse actuelle de rotation progressivement
        if self.turning_speed > MAX_TURNING_SPEED:
            self.turning_speed = MAX_TURNING_SPEED

        if self.turning_speed < MAX_TURNING_SPEED:
            self.turning_speed = min(self.turning_speed + self.acceleration * dt, MAX_TURNING_SPEED)
        else:
            self.turning_speed = max(self.turning_speed - self.acceleration * dt, 0)

        return self.turning_speed


    def calculate_target_angle(self, target_mm_x, target_mm_y):
        self.distance_x_to_target = self.mm_x - target_mm_x
        self.distance_y_to_target = target_mm_y - self.mm_y
        self.distance_to_target = int(math.hypot(self.distance_x_to_target, self.distance_y_to_target))
        print("distance_x:", self.distance_x_to_target, "distance_y:", self.distance_y_to_target)

        self.angle_to_target = int(math.degrees(math.atan2(self.distance_y_to_target, self.distance_x_to_target)))
        self.angle_diff_to_target = self.normalize_angle(self.angle_to_target - self.angle)

        print("target angle:", self.angle_to_target)
        print("angle diff to target:", self.angle_diff_to_target)
        return self.angle_to_target
    
    def calculate_rotation_step(self, dt):
        # Calculer la différence d'angle normalisée
        self.angle_diff_to_target = self.normalize_angle(self.angle_to_target - self.angle)

        # Mettre à jour la vitesse de rotation
        self.update_turning_speed(dt, self.angle_diff_to_target)

        # Limiter la rotation par étape
        max_rotation_step = self.turning_speed * dt
        if abs(self.angle_diff_to_target) < ROTATION_THRESHOLD:
            return self.angle_diff_to_target
        else:
            return max_rotation_step if self.angle_diff_to_target > 0 else -max_rotation_step


    def update_rotation(self, dt):
        rotation_step = self.calculate_rotation_step(dt)
        self.angle += rotation_step
        self.angle = self.normalize_angle(self.angle)
        if self.graphique:
            self.graphique.refesh_graphique()
        return rotation_step

    def move_towards(self, distance_to_target, dt):
        # Mettre à jour la vitesse
        self.update_speed(dt, distance_to_target)

        radians = math.radians(self.angle)
        
        # Calculer les incréments en fonction de la vitesse
        dx = -(math.cos(radians) * self.speed * dt)
        dy = math.sin(radians) * self.speed * dt
        
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
            print("distance step: ", distance_step,"  distance restante: ", distance_to_target, "dt: ", dt)
        self.mm_x += dx
        self.mm_y += dy
        
        if self.graphique:
            self.graphique.refesh_graphique()

        return distance_to_target
    
    def move_backwards(self, distance_to_target, dt):
        # Mettre à jour la vitesse
        self.update_speed(dt, distance_to_target)

        radians = math.radians(self.angle)
        
        # Calculer les incréments en fonction de la vitesse
        dx = (math.cos(radians) * self.speed * dt) # signe inversé car on veut aller en arriere
        dy = -(math.sin(radians) * self.speed * dt) # signe inversé car on veut aller en arriere
        
        # Calculer la distance correspondant à un pas
        distance_step = math.hypot(dx, dy)
        
        # Vérifier si ce pas dépasse la distance restante
        if distance_step >= abs(distance_to_target):
            # Ajuster les incréments pour atteindre exactement la cible
            ratio = distance_to_target / distance_step
            dx *= ratio
            dy *= ratio
            # Distance restante atteinte, on peut arrêter le mouvement
            distance_to_target = 0
        else:
            # Réduire la distance restante
            distance_to_target -= distance_step
            print("distance step: ", distance_step,"  distance restante: ", distance_to_target,  "dt: ", dt)
        self.mm_x += dx
        self.mm_y += dy
        
        if self.graphique:
            self.graphique.refesh_graphique()

        return distance_to_target

    ##########
    ########## FONCTION ASSERVISSEMENT ##########
    ##########

    def avancer(self, distance, ratio_vitesse):
        global MAX_SPEED_MM_S 
        MAX_SPEED_MM_S = MAX_SPEED_MM_S * (ratio_vitesse /100)
        self.distance_to_target = distance
        clock = pygame.time.Clock()
        while self.distance_to_target > DISTANCE_THRESHOLD:
            dt = clock.tick(FPS) / 1000
            self.distance_to_target = self.move_towards(self.distance_to_target, dt)

        MAX_SPEED_MM_S = MAX_SPEED_MM_S * (100 / ratio_vitesse)

        return print("fin foncion avancer")

    def reculer(self, distance, ratio_vitesse):
        global MAX_SPEED_MM_S 
        MAX_SPEED_MM_S = MAX_SPEED_MM_S * (ratio_vitesse/100)
        self.distance_to_target = distance
        clock = pygame.time.Clock()
        while self.distance_to_target > DISTANCE_THRESHOLD:
            dt = clock.tick(FPS) / 1000
            self.distance_to_target = self.move_backwards(self.distance_to_target, dt)

        MAX_SPEED_MM_S = MAX_SPEED_MM_S * (100 / ratio_vitesse)

        return print("fin foncion reculer")
    
    def orienter(self, angle, ratio_vitesse):
        self.angle_to_target = angle
        clock = pygame.time.Clock()
        self.angle_diff_to_target = self.normalize_angle(self.angle_to_target - self.angle)
        while abs(self.angle_diff_to_target) > ROTATION_THRESHOLD:
            dt = clock.tick(FPS) / 1000
            self.update_rotation(dt)

        return print("fin foncion orienter")
    
    def cibler(self, target_mm_x, target_mm_y, ratio_vitesse):
        self.calculate_target_angle(target_mm_x, target_mm_y)
        self.orienter(self.angle_to_target, ratio_vitesse)

        return print("fin foncion cibler")
    
    def rejoindre (self, target_mm_x, target_mm_y, face, ratio_vitesse): # on considère la face 0, c'est la face avant. 
        self.calculate_target_angle(target_mm_x, target_mm_y)
        if face == 1: #si on veut la face arriére
            self.angle_to_target = self.normalize_angle(self.angle_to_target + 180)

        self.orienter(self.angle_to_target, ratio_vitesse)

        if face == 1: # on recule
            self.reculer(self.distance_to_target, ratio_vitesse)
        else: # on avance
            self.avancer(self.distance_to_target, ratio_vitesse)


        return print("fin foncion rejoindre")