import pygame
import math
from robot import Robot, Graphique ,ROTATION_THRESHOLD, DISTANCE_THRESHOLD
from setup import init_pygame,load_image, TABLE_WIDTH_MM, TABLE_HEIGHT_MM, Screen_WIDTH, Screen_HEIGHT
import read_strat_file as rsf
screen = init_pygame()
vinyle, img_width, img_height = load_image()
scaled_vinyle = pygame.transform.scale(vinyle, (Screen_WIDTH, Screen_HEIGHT))

file_strat_path = 'test.txt'

robot = Robot(scaled_vinyle, screen)
###surface###
image_robot = pygame.Surface((robot.px_width, robot.px_height))
image_robot.fill((0,255,0))
image_robot.set_colorkey((0,0,0))

# Dessiner une bande bleue sur l'avant (par exemple, le côté supérieur du rectangle)
band_height = 8  # hauteur de la bande en pixels
pygame.draw.rect(image_robot, (0, 0, 255), (0, 0, robot.px_width, band_height))

rect_robot = image_robot.get_rect()
rect_robot.center = (robot.px_x, robot.px_y)
###surface_fin### 

robot = Robot(scaled_vinyle, screen, image_robot)

target_mm_x = robot.mm_x
target_mm_y = robot.mm_y
target_angle = robot.angle

commands = rsf.parse_fdd_commands(file_strat_path)
print(commands)

a = 1
running = True
#clock = pygame.time.Clock()  # Horloge pour gérer le temps
while running:
    #dt = clock.tick(60) / 1000  # Limite à 60 FPS et conversion en secondes
    #print("dt: ", dt)
    screen.fill((0, 0, 0))
    screen.blit(scaled_vinyle, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            target_px_x, target_px_y = pygame.mouse.get_pos() 
            
            target_mm_x = int ( robot.conversion_From_px_x_To_mm_x(target_px_x))
            target_mm_y = int ( robot.conversion_From_px_y_To_mmy(target_px_y))
            print("target_mm_x: ", target_mm_x, "  target_mm_y: ", target_mm_y)
            target_angle = robot.calculate_target_angle(target_mm_x, target_mm_y)

    #robot.update_rotation(dt)

    #if abs(robot.normalize_angle(target_angle - robot.angle)) < ROTATION_THRESHOLD:
    #    if robot.distance_to_target >=DISTANCE_THRESHOLD :
    #        robot.distance_to_target = robot.move_towards(robot.distance_to_target, dt)
    if a == 1:
        #robot.avancer(100, 100, dt)
        #robot.reculer(100, 100, dt)
        a = 0
    
    if commands:
        function_name, args = commands[0]  # Récupérer la première commande
        if function_name == "avancer":
            # Convertir les arguments en types corrects
            distance = int(args[0])
            ratio_vitesse = int(args[1])
            print("distance_avancer: ", distance, "  ratio_vitesse: ", ratio_vitesse)
            robot.avancer(distance, ratio_vitesse)
        elif function_name == "reculer":
            distance = int(args[0])
            ratio_vitesse = int(args[1])
            print("distance_reculer: ", distance, "  ratio_vitesse: ", ratio_vitesse)
            robot.reculer(distance, ratio_vitesse)

        elif function_name == "orienter":
            angle = int(args[0])
            ratio_vitesse = int(args[1])
            robot.orienter(angle, ratio_vitesse)
            print("angle: ", angle, "  ratio_vitesse: ", ratio_vitesse)

        elif function_name == "cibler":
            target_mm_x = int(args[0])
            target_mm_y = int(args[1])
            ratio_vitesse = int(args[2])
            robot.cibler(target_mm_x, target_mm_y, ratio_vitesse)
            print("target_mm_x: ", target_mm_x, "  target_mm_y: ", target_mm_y, "  ratio_vitesse: ", ratio_vitesse)

        elif function_name == "rejoindre":
            target_mm_x = int(args[0])
            target_mm_y = int(args[1])
            face = int(args[2])
            ratio_vitesse = int(args[3])
            robot.rejoindre(target_mm_x, target_mm_y,face, ratio_vitesse)
            print("target_mm_x: ", target_mm_x, "  target_mm_y: ", target_mm_y, "  face: ", face, "  ratio_vitesse: ", ratio_vitesse)
        else:
            print(f"Fonction {function_name} non reconnue ou non prise en charge.")
        
        commands.pop(0)
    


pygame.quit()
