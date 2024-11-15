import pygame
import math
from robot import Robot
from setup import init_pygame, TABLE_WIDTH_MM, TABLE_HEIGHT_MM, Screen_WIDTH, Screen_HEIGHT

screen = init_pygame()

robot = Robot()
#robot_rectangle = pygame.Rect(robot.px_x, robot.px_y, robot.px_width, robot.px_height)

###surface###
image = pygame.Surface((robot.px_width, robot.px_height))  #pygame.SRCALPHA 
image.fill((0,255,0))
image.set_colorkey((0,0,0))
rect = image.get_rect()  # Crée un rect pour le rectangle
rect.center = (robot.px_x, robot.px_y)  # Définit une position initiale

rotated_image = image # variable global 
rotated_rect = rect # variable global
###surafce_fin###  

### debug###
font = pygame.font.Font(None, 36)
target_mm_x = 0
target_mm_y = 0
orientation = 0
####debug_fin###

running = True
rotation_to_do_relatif, angle_objectif_absolue, distance = 0, 0, 0
angle_diff = 0
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            target_px_x, target_px_y = pygame.mouse.get_pos() 
            
            target_mm_x = (Screen_WIDTH - target_px_x) * (TABLE_WIDTH_MM / Screen_WIDTH) #target_px_x = Screen_WIDTH - target_px_x # symétrie car par default le point d'origine est en bas à gauche
            target_mm_y = (Screen_HEIGHT - target_px_y) * (TABLE_HEIGHT_MM / Screen_HEIGHT)

            rotation_to_do_relatif, angle_objectif_absolue, distance = robot.calculate_target_angle_relatif_absolu_distance(target_mm_x, target_mm_y)

    angle_diff = (angle_objectif_absolue - robot.angle + 180) % 360 - 180   
    ###test###
    if   ( abs(angle_diff) > 1 ):
        robot.angle += 1 * (1 if rotation_to_do_relatif > 0 else -1)
    else:
        robot.angle = angle_objectif_absolue
        print("distance: ", distance)

        ### Mise à jour graphique ###

    rotated_image = pygame.transform.rotate(image, -robot.angle)  # on change le signe car la trigonometrie est en sens horaire et la fonction pygame.transform.rotate est en sens anti-horaire
    rotated_rect = rotated_image.get_rect(center=rect.center) 
    
    #robot_rectangle.center = (robot.px_x, robot.px_y,)
    #print("initial_mm_x :",robot.mm_x,"initial_mm_y :",robot.mm_y,"initial_px_x :",robot.px_x,"initial_px_y :",robot.px_y)
    ###test fin###

    screen.blit(rotated_image, rotated_rect) 
    #pygame.draw.rect(screen, (255, 0, 0), robot_rectangle)
    
    
    ##debug##
    coords_text = font.render(f"X: {int(target_mm_x)} mm, Y: {int(target_mm_y)} mm, O: {int(orientation)}", True, (255, 255, 255))
    screen.blit(coords_text, (10, 10))  # Position du texte en haut à gauche
    ##debug_fin##

    pygame.display.flip()

pygame.quit()