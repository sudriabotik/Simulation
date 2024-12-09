import math
import pygame
import time
from enum import Enum

from setup import TABLE_WIDTH_MM, TABLE_HEIGHT_MM, Screen_WIDTH, Screen_HEIGHT
import Converter

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
        self.robot.angle_px = Converter.conversion_trigo_transform_rotate(self.robot.angle) 
        self.robot.px_x = Converter.conversion_From_mmx_To_px_x(self.robot.mm_x)
        self.robot.px_y = Converter.conversion_From_mmy_To_px_y(self.robot.mm_y)

        rotated_image = pygame.transform.rotate(self.image_robot, self.robot.angle_px)
        robot_rect = rotated_image.get_rect(center=(self.robot.px_x, self.robot.px_y))
        self.screen.blit(rotated_image, robot_rect)

        coords_text = self.font.render(f"X: {int(self.robot.mm_x)} mm, Y: {int(self.robot.mm_y)} mm, O: {int(self.robot.angle)}", True, (255, 255, 255))
        self.screen.blit(coords_text, (10, 10))  # Position du texte en haut à gauche

        

class MovementState(Enum) :
    IDLE = 0
    TRANSLATE = 1
    ROTATE = 2

class Translation :
    def __init__(self) :
        self.maxSpeed = 0
        # target final position (in mm)
        self.finalPos = (0, 0)
        # unit vector in the direction of the translation (in robot space)
        self.direction = (0, 0)
        self.rampingTime = 0
        self.rampingDistance = 0


class RobotNonBloc :


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

        # variables to keep track of current movement type and its properties
        self.currentState = MovementState.IDLE
        self.movementTarger = None
        self.movementArgs = None

        # variables for the update loop
        self.updateLoopClock = pygame.time.Clock()

        if image_robot and screen and scaled_vinyle:
            self.graphique = Graphique(self, image_robot, screen, scaled_vinyle)
        else:
            self.graphique = None  # Si l'image ou l'écran manque, pas de rendu graphique
            print("erreur, missing arg: image ou screen")

    
    def updateGraphics(self) :
        self.graphique.refesh_graphique()

    def getIfBusy(self) :
        return self.currentState != MovementState.IDLE
    
    def update_translation_target_speed(self, distance):
        # Calculate the deceleration distance based on the robot's max speed and acceleration
        deceleration_distance = self.movementArgs.rampingDistance

        if distance <= deceleration_distance :
            # Reduce speed proportionally to the remaining distance
            self.target_speed = max(0, (distance / deceleration_distance) * self.movementArgs.maxSpeed)
        else:
            # Maintain maximum speed
            self.target_speed = self.movementArgs.maxSpeed
    
    def update_translation_speed(self, dt, distance_restante):
        #distance_restante = abs(distance_restante) # pour gérer les valeur négative
        self.update_translation_target_speed(distance_restante)  # Met à jour la vitesse cible en fonction de la distance
        if self.speed < self.target_speed:
            self.speed = min(self.speed + self.acceleration * dt, self.target_speed)
            #print("update_augmentation_speed: ", self.speed)
        elif self.speed > self.target_speed:
            self.speed = max(self.speed - self.acceleration * dt, self.target_speed)
            #print("update_diminution_speed: ", self.speed)
    
    def updatePosition(self) :
        #print(self.currentState)
        # dt in seconds
        dt = self.updateLoopClock.tick(FPS) / 1000
        if self.currentState == MovementState.TRANSLATE :

            distance_to_target = int(math.hypot(self.mm_x - self.movementArgs.finalPos[0], self.mm_y - self.movementArgs.finalPos[1]))

            # means the translation is done
            if distance_to_target < DISTANCE_THRESHOLD :
                self.currentState = MovementState.IDLE
                return
            

            self.update_translation_speed(dt, distance_to_target)

            # prevents overshooting of the target
            if self.speed * dt > distance_to_target :
                self.speed = self.speed * (distance_to_target/(self.speed*dt))
            
            
            self.mm_x += self.movementArgs.direction[0] * self.speed * dt
            self.mm_y += self.movementArgs.direction[1] * self.speed * dt

            

            
            
    
    
    """For a translation, return how much distance and time will be spent at the beginning or end in the ramping state. Max speed in mm/s"""
    def getRampingDistance(self, totalTranslationDistance, maxSpeed) :
        rampingTime = MAX_SPEED_MM_S / maxSpeed
        rampingDistance = (maxSpeed ** 2) / (2 * MAX_ACCEL_MM_S2)

        if rampingDistance > totalTranslationDistance/2 :
            ratio = ((totalTranslationDistance/2)/rampingDistance)
            rampingTime = rampingTime * ratio
            rampingDistance = totalTranslationDistance / 2
        
        return rampingDistance, rampingTime
    
    '''Unused function'''
    def estimateTimeNeededForTranslation(self, distance) :

        rampingDistance, rampingTime = self.getRampingDistance(distance)        

        totalTime = rampingTime * 2 + (distance - rampingDistance*2) / MAX_SPEED_MM_S
        return totalTime
    

    
    def translate(self, distance, speedPercent = 100) :
        print("new translation")
        if self.getIfBusy() :
            return
        
        direction = 1
        if distance < 0 :
            direction = -1
        distance = abs(distance)
        print(direction)
        print(distance)
        
        self.currentState = MovementState.TRANSLATE

        
        self.movementArgs = Translation()
        self.movementArgs.maxSpeed = (MAX_SPEED_MM_S / 100) * speedPercent
        self.movementArgs.direction = (math.cos(self.angle/180*math.pi) * direction, math.sin(self.angle/180*math.pi) * direction)
        print(self.movementArgs.direction)
        self.movementArgs.finalPos = (self.mm_x + self.movementArgs.direction[0]*distance, self.mm_y + self.movementArgs.direction[1]*distance)
        self.movementArgs.rampingDistance, self.movementArgs.rampingTime = self.getRampingDistance(distance, self.movementArgs.maxSpeed)
        

        # resets the value of dt in the update loop since it is the start of a new movement
        self.updateLoopClock.tick()

        print(self.movementArgs.maxSpeed)
    
    