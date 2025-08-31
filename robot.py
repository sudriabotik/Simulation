import math
import pygame
from setup import TABLE_WIDTH_MM, TABLE_HEIGHT_MM, FIELD_HEIGHT, FIELD_WIDTH
# Robot specifications
ROBOT_WIDTH_MM = 320
ROBOT_HEIGHT_MM = 290
init_x_mm = 300
init_y_mm = 950
init_angle = 0

# Vitesse maximale en mm/s
# Accélération maximale en mm/s^2
# Vitesse de rotation en degrés par seconde
# Accélération angulaire maximale en degrés par seconde
max_speed_mm_s  = 1000
max_accel_mm_s2 = 2000
max_turning_speed = 500
max_turning_accel = 300

ROTATION_THRESHOLD = 1
DISTANCE_THRESHOLD = 1

FPS = 60

def create_robot_surface():
    px_width = (ROBOT_WIDTH_MM / TABLE_WIDTH_MM) * FIELD_WIDTH
    px_height = (ROBOT_HEIGHT_MM / TABLE_HEIGHT_MM) * FIELD_HEIGHT
    px_x = ((TABLE_WIDTH_MM - init_x_mm) / TABLE_WIDTH_MM) * FIELD_WIDTH
    px_y = ((TABLE_HEIGHT_MM - init_y_mm) / TABLE_HEIGHT_MM) * FIELD_HEIGHT
    band_height = 8  # hauteur de la bande en pixels

    image_robot = pygame.Surface((px_width, px_height))
    image_robot.fill((0, 255, 0))
    image_robot.set_colorkey((0, 0, 0))
    pygame.draw.rect(image_robot, (0, 0, 255), (0, 0, px_width, band_height))
    rect_robot = image_robot.get_rect()
    rect_robot.center = (px_x, px_y)
    return image_robot, rect_robot

class Graphique:
    def __init__(self, robot, image_robot, screen, scaled_vinyle):
        self.robot = robot  # Référence à l'instance de Robot existante
        self.image_robot = image_robot
        self.screen = screen
        self.font = pygame.font.Font(None, 18)# taille du text réduite
        self.chrono_font = pygame.font.Font(None, 24)# police pour le chronomètre
        self.scaled_vinyle = scaled_vinyle
        self.strategy_start_time = 0
        self.strategy_elapsed_time = 0

    def update_strategy_time(self, current_time, strategy_active):
        if strategy_active and self.strategy_start_time == 0:
            self.strategy_start_time = current_time
        elif strategy_active and self.strategy_start_time > 0:
            self.strategy_elapsed_time = current_time - self.strategy_start_time
        elif not strategy_active:
            self.strategy_start_time = 0
            self.strategy_elapsed_time = 0
    
    def refesh_graphique(self):
        # Remplir uniquement la zone du terrain (FIELD_WIDTH x FIELD_HEIGHT) en noir
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(0, 0, FIELD_WIDTH, FIELD_HEIGHT))
        self.screen.blit(self.scaled_vinyle, (0, 0))
        self.robot.angle_px =self.robot.conversion_trigo_transform_rotate(self.robot.angle) 
        self.robot.px_x = self.robot.conversion_From_mmx_To_px_x(self.robot.mm_x)
        self.robot.px_y = self.robot.conversion_From_mmy_To_px_y(self.robot.mm_y)

        rotated_image = pygame.transform.rotate(self.image_robot, self.robot.angle_px)
        robot_rect = rotated_image.get_rect(center=(self.robot.px_x, self.robot.px_y))
        self.screen.blit(rotated_image, robot_rect)

        # Affichage de la position du robot à gauche de la sidebar
        coords_text = self.font.render(f"X: {int(self.robot.mm_x)} mm, Y: {int(self.robot.mm_y)} mm, O: {int(self.robot.angle)}", True, (255, 255, 255))
        self.screen.blit(coords_text, (910, 10))  # Position à gauche de la sidebar
        
        # Affichage du chronomètre à droite de la sidebar
        chrono_text = self.chrono_font.render(f"{int(self.strategy_elapsed_time)}s", True, (255, 255, 0))
        chrono_width = chrono_text.get_width()
        self.screen.blit(chrono_text, (1200 - chrono_width - 10, 10))  # Position à droite de la sidebar

        pygame.display.update()

class Robot(Graphique):
    clock = pygame.time.Clock()
    def __init__(self,scaled_vinyle=None, screen=None, image_robot= None, x= init_x_mm, y= init_y_mm, angle=init_angle, speed=0):
        self.mm_x = x
        self.mm_y = y 
        self.px_x = ((TABLE_WIDTH_MM - x) /TABLE_WIDTH_MM)*FIELD_WIDTH #Due to the origin point on the top left, we need to invert the axis: 
        self.px_y = ((TABLE_HEIGHT_MM - y)/TABLE_HEIGHT_MM)*FIELD_HEIGHT# valeur de x en pixel
        self.angle = angle
        self.angle_px = angle - 90
        self.angle_to_target = angle
        self.angle_diff_to_target = 0
        self.distance_x_to_target = 0
        self.distance_y_to_target = 0
        self.distance_to_target = 0
        self.speed = speed  # Vitesse actuelle en mm/s
        self.max_speed = max_speed_mm_s
        self.acceleration = max_accel_mm_s2
        self.turning_speed = 0  # En degrés par seconde
        self.max_turning_speed = max_turning_speed
        self.turning_acceleration = max_turning_accel
        self.target_speed = 0  # Vitesse cible

        self.px_width = (ROBOT_WIDTH_MM/TABLE_WIDTH_MM)*FIELD_WIDTH
        self.px_height = (ROBOT_HEIGHT_MM/TABLE_HEIGHT_MM)*FIELD_HEIGHT
        self.mm_width = ROBOT_WIDTH_MM
        self.mm_height = ROBOT_HEIGHT_MM

        if image_robot and screen and scaled_vinyle:
            self.graphique = Graphique(self, image_robot, screen, scaled_vinyle)
        else:
            self.graphique = None  # Si l'image ou l'écran manque, pas de rendu graphique
            print("erreur, missing arg: image ou screen")


    def conversion_From_mmx_To_px_x(self, mm_x):
        px_x = ((TABLE_WIDTH_MM - mm_x) /TABLE_WIDTH_MM)*FIELD_WIDTH
        return px_x
    
    def conversion_From_mmy_To_px_y(self, mm_y):
        px_y = ((TABLE_HEIGHT_MM - mm_y)/TABLE_HEIGHT_MM)*FIELD_HEIGHT
        return px_y

    def conversion_From_px_x_To_mm_x(self, px_x):
        x_mm = (FIELD_WIDTH - px_x) * (TABLE_WIDTH_MM / FIELD_WIDTH)
        return x_mm
    
    def conversion_From_px_y_To_mmy(self, px_y):
        y_mm = (FIELD_HEIGHT - px_y) * (TABLE_HEIGHT_MM / FIELD_HEIGHT)
        return y_mm

    def conversion_trigo_transform_rotate(self, angle):
        angle_px = (angle-90)
        return angle_px
    
    def normalize_angle(self, angle):
        angle = angle % 360  
        if angle > 180:
            angle -= 360  
        return angle

    def update_speed_trapezoidal(self, dt, distance_restante):

        v_max = self.max_speed
        a = self.acceleration

        # Distance pour accélérer et décélérer
        d_accel = (v_max ** 2) / (2 * a) # 266
        d_decel = d_accel

        # Vitesse max atteignable
        if distance_restante < (d_accel + d_decel):
            v_peak = math.sqrt(a * distance_restante)
            # il faut limiter v_peak par v_max
            if v_peak > v_max:
                v_peak = v_max
        else:
            v_peak = v_max

        d_brake = (self.speed ** 2) / (2 * a)

        # Accélération
        if self.speed < v_peak and distance_restante > d_brake:
            self.speed = min(self.speed + a * dt, v_peak)
            print("acceleration")
        # Décélération uniquement si on est proche de la cible ET que la vitesse > 0
        elif distance_restante <= d_brake and self.speed > 0:
            self.speed = max(self.speed - a * dt, 0)
            print("deceleration")
        # Plateau
        elif self.speed >= v_peak:
            self.speed = v_peak
            print("plateau")
        else:
            print("rien .....")

        # Correction : si la distance restante est très faible, forcer la vitesse à zéro
        if distance_restante < DISTANCE_THRESHOLD:
            self.speed = 0

        print("d_accel: ", d_accel, "v_peak: ", v_peak)


    def update_turning_speed(self, dt, angle_diff_restante):

        w_max = self.max_turning_speed         # Vitesse angulaire maximale [°/s]
        alpha = self.turning_acceleration         # Accélération angulaire [°/s²]

        # Distance angulaire pour accélérer ou décélérer (symétrique)
        d_accel = (w_max ** 2) / (2 * alpha)  # En degrés
        d_decel = d_accel

        # Vitesse atteignable en fonction de l'angle restant
        w_peak = math.sqrt(2 * alpha * abs(angle_diff_restante))
        w_peak = min(w_peak, w_max)

        # Distance de freinage à partir de la vitesse actuelle
        d_brake = (self.turning_speed ** 2) / (2 * alpha)

        # Phase d'accélération
        if self.turning_speed < w_peak and abs(angle_diff_restante) > d_brake:
            self.turning_speed = min(self.turning_speed + alpha * dt, w_peak)
            print("accélération angulaire")

        # Phase de décélération
        elif abs(angle_diff_restante) <= d_brake and self.turning_speed > 0:
            self.turning_speed = max(self.turning_speed - alpha * dt, 0)
            print("décélération angulaire")

        # Plateau
        elif self.turning_speed >= w_peak:
            self.turning_speed = w_peak
            print("plateau angulaire")

        else:
            print("rien ... (rotation)")

        # Arrêt complet si angle trop faible
        if abs(angle_diff_restante) < ROTATION_THRESHOLD:
            self.turning_speed = 0

        print(f"d_accel: {d_accel:.2f}, w_peak: {w_peak:.2f}, turning_speed: {self.turning_speed:.2f}? angle_diff_restante: {angle_diff_restante:.2f}")


    def calculate_target_angle(self, target_mm_x, target_mm_y):
        self.distance_x_to_target = self.mm_x - target_mm_x
        self.distance_y_to_target = target_mm_y - self.mm_y
        self.distance_to_target = math.hypot(self.distance_x_to_target, self.distance_y_to_target)  # Garder la précision
        print("distance_x:", self.distance_x_to_target, "distance_y:", self.distance_y_to_target)

        self.angle_to_target = math.degrees(math.atan2(self.distance_y_to_target, self.distance_x_to_target))  # Garder la précision
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
        self.update_speed_trapezoidal(dt, distance_to_target)

        radians = math.radians(self.angle)
        
        # Calculer les incréments en fonction de la vitesse
        dx = -(math.cos(radians) * self.speed * dt)
        dy = math.sin(radians) * self.speed * dt
        
        # Calculer la distance correspondant à un pas
        distance_step = math.hypot(dx, dy)
        
        # Vérifier si ce pas dépasse la distance restante
        if distance_step >= distance_to_target:
            # Ajuster les incréments pour atteindre exactement la cible
            if distance_step > 0:  # Éviter division par zéro
                ratio = distance_to_target / distance_step
                dx *= ratio
                dy *= ratio
            # Distance restante atteinte, on peut arrêter le mouvement
            distance_to_target = 0
        else:
            # Réduire la distance restante
            distance_to_target -= distance_step
            print("distance step: ", distance_step,"  distance restante: ", distance_to_target,"self.speed: ", self.speed, "dt: ", dt)
        self.mm_x += dx
        self.mm_y += dy
        
        if self.graphique:
            self.graphique.refesh_graphique()

        return distance_to_target
    
    def move_backwards(self, distance_to_target, dt):
        # Mettre à jour la vitesse
        self.update_speed_trapezoidal(dt, distance_to_target)

        radians = math.radians(self.angle)
        
        # Calculer les incréments en fonction de la vitesse
        dx = (math.cos(radians) * self.speed * dt) # signe inversé car on veut aller en arriere
        dy = -(math.sin(radians) * self.speed * dt) # signe inversé car on veut aller en arriere
        
        # Calculer la distance correspondant à un pas
        distance_step = math.hypot(dx, dy)
        
        # Vérifier si ce pas dépasse la distance restante
        if distance_step >= abs(distance_to_target):
            # Ajuster les incréments pour atteindre exactement la cible
            if distance_step > 0:  # Éviter division par zéro
                ratio = distance_to_target / distance_step
                dx *= ratio
                dy *= ratio
            # Distance restante atteinte, on peut arrêter le mouvement
            distance_to_target = 0
        else:
            # Réduire la distance restante
            distance_to_target -= distance_step
            print("distance step: ", distance_step,"  distance restante: ", distance_to_target,"self.speed: ", self.speed, "dt: ", dt)
        self.mm_x += dx
        self.mm_y += dy
        
        if self.graphique:
            self.graphique.refesh_graphique()

        return distance_to_target

    ##########
    ########## FONCTION ASSERVISSEMENT ##########
    ##########

    def avancer(self, distance, ratio_vitesse):
        #global self.max_speed 
        self.max_speed = self.max_speed * (ratio_vitesse /100)
        self.distance_to_target = distance
        clock = pygame.time.Clock()
        while self.distance_to_target > DISTANCE_THRESHOLD:
            dt = clock.tick(FPS) / 1000
            self.distance_to_target = self.move_towards(self.distance_to_target, dt)

        self.max_speed = self.max_speed * (100 / ratio_vitesse)

        return print("fin foncion avancer")

    def reculer(self, distance, ratio_vitesse):
        #global self.max_speed 
        self.max_speed = self.max_speed * (ratio_vitesse/100)
        self.distance_to_target = distance
        clock = pygame.time.Clock()
        while self.distance_to_target > DISTANCE_THRESHOLD:
            dt = clock.tick(FPS) / 1000
            self.distance_to_target = self.move_backwards(self.distance_to_target, dt)

        self.max_speed = self.max_speed * (100 / ratio_vitesse)

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
        # Calcul initial de l'angle et de la distance
        self.calculate_target_angle(target_mm_x, target_mm_y)
        if face == 1: #si on veut la face arriére
            self.angle_to_target = self.normalize_angle(self.angle_to_target + 180)

        # Orientation vers la cible
        self.orienter(self.angle_to_target, ratio_vitesse)

        # Recalculer la distance exacte après rotation pour corriger les erreurs
        distance_x = self.mm_x - target_mm_x
        distance_y = target_mm_y - self.mm_y
        distance_exacte = math.hypot(distance_x, distance_y)
        
        print(f"Distance recalculée après rotation: {distance_exacte:.2f} mm")

        if face == 1: # on recule
            self.reculer(distance_exacte, ratio_vitesse)
        else: # on avance
            self.avancer(distance_exacte, ratio_vitesse)

        # Vérification finale de la position
        final_distance_x = self.mm_x - target_mm_x
        final_distance_y = target_mm_y - self.mm_y
        final_error = math.hypot(final_distance_x, final_distance_y)
        print(f"Erreur finale de positionnement: {final_error:.2f} mm")

        return print("fin foncion rejoindre")