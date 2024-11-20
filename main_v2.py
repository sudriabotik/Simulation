import pygame
import math
import robot
from robot import Robot 
from setup import init_pygame,load_image, TABLE_WIDTH_MM, TABLE_HEIGHT_MM, Screen_WIDTH, Screen_HEIGHT

screen = init_pygame()
vinyle, img_width, img_height = load_image()
scaled_vinyle = pygame.transform.scale(vinyle, (Screen_WIDTH, Screen_HEIGHT))
robot = Robot()

###surface###
image_robot = pygame.Surface((robot.px_width, robot.px_height))  #pygame.SRCALPHA 
image_robot.fill((0,255,0))
image_robot.set_colorkey((0,0,0))
rect_robot = image_robot.get_rect()  # Crée un rect pour le rectangle
rect_robot.center = (robot.px_x, robot.px_y)  # Définit une position initiale
###surafce_fin###  

### debug###
font = pygame.font.Font(None, 36)
####debug_fin###

#target_mm_x = 0
#target_mm_y = 0
target_angle = robot.angle

def normalize_angle(angle):
    angle = angle % 360  
    if angle > 180:
        angle -= 360  
    return angle

running = True

while running:
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

    angle_diff = normalize_angle(target_angle - robot.angle) 
    
    if   ( abs(angle_diff) >= 1 ):
        robot.angle += 1 * (1 if angle_diff > 0 else -1)
        robot.angle = normalize_angle(robot.angle)
        print("rotation // angle_diff:", angle_diff, "   robot.angle:", robot.angle)
    else:
        if robot.distance_to_target >=1 :
            robot.distance_to_target =robot.move_towards(robot.distance_to_target)
        
        ### Mise à jour graphique ###
    robot.angle_px = robot.conversion_trigo_transform_rotate(robot.angle) 
    robot.px_x = robot.conversion_From_mmx_To_px_x(robot.mm_x)
    robot.px_y = robot.conversion_From_mmy_To_px_y(robot.mm_y)    
    rect_robot = image_robot.get_rect(center=(robot.px_x, robot.px_y))
    rotated_image = pygame.transform.rotate(image_robot, robot.angle_px) 
    rotated_rect = rotated_image.get_rect(center=rect_robot.center) 
    screen.blit(rotated_image, rotated_rect) 
    
    ##debug##
    coords_text = font.render(f"X: {int(robot.mm_x)} mm, Y: {int(robot.mm_y)} mm, O: {int(robot.angle)}", True, (255, 255, 255))
    screen.blit(coords_text, (10, 10))  # Position du texte en haut à gauche
    font = pygame.font.Font(None, 36)

    #pygame.display.flip() # ça ralentie l'affichage
    pygame.display.update()

pygame.quit()
