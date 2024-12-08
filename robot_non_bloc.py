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
        self.robot.angle_px = Converter.conversion_trigo_transform_rotate(self.robot.angle) 
        self.robot.px_x = Converter.conversion_From_mmx_To_px_x(self.robot.mm_x)
        self.robot.px_y = Converter.conversion_From_mmy_To_px_y(self.robot.mm_y)

        rotated_image = pygame.transform.rotate(self.image_robot, self.robot.angle_px)
        robot_rect = rotated_image.get_rect(center=(self.robot.px_x, self.robot.px_y))
        self.screen.blit(rotated_image, robot_rect)

        coords_text = self.font.render(f"X: {int(self.robot.mm_x)} mm, Y: {int(self.robot.mm_y)} mm, O: {int(self.robot.angle)}", True, (255, 255, 255))
        self.screen.blit(coords_text, (10, 10))  # Position du texte en haut à gauche

        pygame.display.update()

class MovementState(Enum) :
    IDLE = 0
    TRANSLATE = 1
    ROTATE = 2

class Movement :

    def __init__(self) :
        self.timeStart = time.time()

class Translation(Movement) :

    def __init__(self) :
        self.initialPos = (0, 0) # x and y in millimeter
        self.finalPos = (0, 0) # x and y in millimeter
        self.movementDirection = (0, 0) # unit vector in the direction of the movement
        self.totalDistance = 0

        self.rampingTime = 0
        self.rampingDistance = 0
        self.totalTime = 0
    
    def __str__(self) -> str:
        return f"start ({self.initialPos[0]}, {self.initialPos[1]}) ; end ({self.finalPos[0]}, {self.finalPos[1]}) ; ramping time {self.rampingTime}s ; rampingDistance {self.rampingDistance}mm"

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
        self.movementTimeStart = 0 # in seconds
        # contains a child of the Movement class. Used to store various info about the current motion being executed, None otherwise
        self.movementArgs = None

        if image_robot and screen and scaled_vinyle:
            self.graphique = Graphique(self, image_robot, screen, scaled_vinyle)
        else:
            self.graphique = None  # Si l'image ou l'écran manque, pas de rendu graphique
            print("erreur, missing arg: image ou screen")

    
    def updateGraphics(self) :
        self.graphique.refesh_graphique()

    def getIfBusy(self) :
        return self.currentState != MovementState.IDLE
    
    def updatePosition(self) :
        print(self.currentState)
        if self.currentState == MovementState.TRANSLATE :
            timeElapsed = time.time() - self.movementTimeStart
            print(self.movementArgs.totalTime)
            # check if we are in the start ramp, steady speed or braking ramp
            if timeElapsed < self.movementArgs.rampingTime :
                distanceFromStart = self.getDistanceCoveredFromAccel(timeElapsed)
            elif timeElapsed < self.movementArgs.totalTime - self.movementArgs.rampingTime :
                distanceFromStart = self.movementArgs.rampingDistance + MAX_SPEED_MM_S * (timeElapsed - self.movementArgs.rampingTime)
            elif timeElapsed < self.movementArgs.totalTime :
                distanceFromStart = self.movementArgs.totalDistance - self.getDistanceCoveredFromAccel(self.movementArgs.totalTime - timeElapsed)
            else :
                self.movementArgs = None
                self.currentState = MovementState.IDLE
                return
                
            print(timeElapsed)
            self.mm_x = self.movementArgs.initialPos[0] + self.movementArgs.movementDirection[0] * distanceFromStart
            self.mm_y = self.movementArgs.initialPos[1] + self.movementArgs.movementDirection[1] * distanceFromStart
    
    def getDistanceCoveredFromAccel(self, t) :
        return ((t**2)/2)*MAX_ACCEL_MM_S2    

    
    def translate(self, distance, speedPercent = 100) :
        if self.getIfBusy() :
            return
        
        direction = 1
        if distance < 0 :
            direction = -1
        distance = abs(distance)
        
        self.currentState = MovementState.TRANSLATE

        desiredSpeed = (MAX_SPEED_MM_S / 100) * speedPercent

        # calculate on what distance the robot need to accelerate to reach the desired speed

        #rampingDistance = (desiredSpeed ** 2) / (2 * MAX_ACCEL_MM_S2)
        rampingTime = MAX_SPEED_MM_S / MAX_ACCEL_MM_S2
        rampingDistance = self.getDistanceCoveredFromAccel(rampingTime)

        if rampingDistance > distance/2 :
            ratio = ((distance/2)/rampingDistance)
            rampingTime = rampingTime * ratio
            rampingDistance = distance / 2
        
        totalTime = rampingTime * 2 + (distance - rampingDistance*2) / MAX_SPEED_MM_S

        self.movementArgs = Translation()
        self.movementArgs.totalDistance = distance
        self.movementArgs.initialPos = (self.mm_x, self.mm_y)
        self.movementArgs.finalPos = (self.mm_x + math.cos(self.angle/180*math.pi)*distance, self.mm_y + math.sin(self.angle/180*math.pi)*distance)
        self.movementArgs.rampingTime = rampingTime
        self.movementArgs.rampingDistance = rampingDistance
        self.movementArgs.totalTime = totalTime
        self.movementArgs.movementDirection = (math.cos(self.angle) * direction, math.sin(self.angle) * direction)
        
        self.movementTimeStart = time.time()
        
        print(self.movementArgs)
    
    

testBot = RobotNonBloc()

testBot.translate(100)