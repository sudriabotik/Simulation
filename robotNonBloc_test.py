import pygame
import math
from robot import Robot, Graphique ,ROTATION_THRESHOLD, DISTANCE_THRESHOLD
from robot_non_bloc import RobotNonBloc
from setup import init_pygame,load_image, TABLE_WIDTH_MM, TABLE_HEIGHT_MM, Screen_WIDTH, Screen_HEIGHT
import read_strat_file as rsf
screen = init_pygame()
vinyle, img_width, img_height = load_image()
scaled_vinyle = pygame.transform.scale(vinyle, (Screen_WIDTH, Screen_HEIGHT))

file_strat_path = 'test.txt'

robot = RobotNonBloc(scaled_vinyle, screen)
###surface###
image_robot = pygame.Surface((robot.px_width, robot.px_height))  #pygame.SRCALPHA 
image_robot.fill((0,255,0))
image_robot.set_colorkey((0,0,0))
rect_robot = image_robot.get_rect()  # Crée un rect pour le rectangle
rect_robot.center = (robot.px_x, robot.px_y)  # Définit une position initiale
###surafce_fin###  

robot = RobotNonBloc(scaled_vinyle, screen, image_robot)
robot2 = RobotNonBloc(scaled_vinyle, screen, image_robot)

target_mm_x = robot.mm_x
target_mm_y = robot.mm_y
target_angle = robot.angle

a = 1
running = True
#clock = pygame.time.Clock()  # Horloge pour gérer le temps
while running:

    screen.fill((0, 0, 0))
    screen.blit(scaled_vinyle, (0, 0))
    

    #dt = clock.tick(60) / 1000  # Limite à 60 FPS et conversion en secondes
    #print("dt: ", dt)
    screen.fill((0, 0, 0))
    screen.blit(scaled_vinyle, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #robot.update_rotation(dt)

    #if abs(robot.normalize_angle(target_angle - robot.angle)) < ROTATION_THRESHOLD:
    #    if robot.distance_to_target >=DISTANCE_THRESHOLD :
    #        robot.distance_to_target = robot.move_towards(robot.distance_to_target, dt)
    if a == 1 and not robot.getIfBusy() :
        print("first translation")
        robot.translate(1000, 100)
        a = 2
    elif a == 2 and not robot.getIfBusy() :
        print("second translation")
        robot.translate(-1000, 50)
        robot2.translate(1000, 80)
        a = 0
    
    robot.updatePosition()
    robot.updateGraphics()
    robot2.updatePosition()
    robot2.updateGraphics()

    pygame.display.update()
    


pygame.quit()
