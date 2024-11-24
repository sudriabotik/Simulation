import pygame
import math
import robot
from robot import Robot, Graphique ,ROTATION_THRESHOLD
from setup import init_pygame,load_image, TABLE_WIDTH_MM, TABLE_HEIGHT_MM, Screen_WIDTH, Screen_HEIGHT

screen = init_pygame()
vinyle, img_width, img_height = load_image()
scaled_vinyle = pygame.transform.scale(vinyle, (Screen_WIDTH, Screen_HEIGHT))

robot = Robot(screen)
###surface###
image_robot = pygame.Surface((robot.px_width, robot.px_height))  #pygame.SRCALPHA 
image_robot.fill((0,255,0))
image_robot.set_colorkey((0,0,0))
rect_robot = image_robot.get_rect()  # Crée un rect pour le rectangle
rect_robot.center = (robot.px_x, robot.px_y)  # Définit une position initiale
###surafce_fin###  

robot = Robot(screen=screen, image_robot=image_robot)

target_mm_x = robot.mm_x
target_mm_y = robot.mm_y
target_angle = robot.angle

running = True
clock = pygame.time.Clock()  # Horloge pour gérer le temps
while running:
    dt = clock.tick(60) / 1000  # Limite à 60 FPS et conversion en secondes
    #print("dt: ", dt)
    screen.fill((0, 0, 0))
    screen.blit(scaled_vinyle, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            target_px_x, target_px_y = pygame.mouse.get_pos() 
            
            target_mm_x = int (  robot.conversion_From_px_x_To_mm_x(target_px_x))
            target_mm_y = int ( robot.conversion_From_px_y_To_mmy(target_px_y))
            print("target_mm_x: ", target_mm_x, "  target_mm_y: ", target_mm_y)
            target_angle = robot.calculate_target_angle(target_mm_x, target_mm_y)

    robot.update_rotation(dt)

    if abs(robot.normalize_angle(target_angle - robot.angle)) < ROTATION_THRESHOLD:
        if robot.distance_to_target >=1 :
            robot.distance_to_target = robot.move_towards(robot.distance_to_target, dt)

        ### Mise à jour graphique ###
    #robot.angle_px = robot.conversion_trigo_transform_rotate(robot.angle) 
    #robot.px_x = robot.conversion_From_mmx_To_px_x(robot.mm_x)
    #robot.px_y = robot.conversion_From_mmy_To_px_y(robot.mm_y)

    #rotated_image = pygame.transform.rotate(image_robot, robot.angle_px) 
    #robot_rect = rotated_image.get_rect(center=(robot.px_x, robot.px_y)) 
    #screen.blit(rotated_image, robot_rect) 
    #graphique.refesh_graphique()

    ##debug##
    #coords_text = font.render(f"X: {int(robot.mm_x)} mm, Y: {int(robot.mm_y)} mm, O: {int(robot.angle)}", True, (255, 255, 255))
    #screen.blit(coords_text, (10, 10))  # Position du texte en haut à gauche

    #pygame.display.update()

pygame.quit()
