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

rotated_image = image_robot # variable global 
rotated_rect = rect_robot # variable global
###surafce_fin###  

### debug###
font = pygame.font.Font(None, 36)
####debug_fin###

target_mm_x = 0
target_mm_y = 0
target_angle = robot.angle
orientation = 0

### rectification_debut #########
dx, dy = 0, 0
speed = 3
clock = pygame.time.Clock()
angle_input = ""  # Variable pour stocker la saisie clavier
distance_to_do = 0
### rectification_fin #########

def set_direction(angle_target, distance=100):
    global dx, dy
    radians = math.radians(angle_target)
    #!!!!!!
    dx = -( math.cos(radians) * speed) #!!!! on inverse le signe car l'axe des x sur le terrain est inversé par rapport au cercle trigo. 
    dy = math.sin(radians) * speed# simplement une valeur entre 1 et -1 pour définir le signe
    print("dx:", dx, "  dy:", dy) 

def normalize_angle(angle):
    angle = angle % 360  
    if angle > 180:
        angle -= 360  
    return angle

running = True
rotation_to_do_relatif, angle_objectif_absolue, distance = 0, 0, 0
angle_diff = 0
while running:
    screen.fill((0, 0, 0))
    screen.blit(scaled_vinyle, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            target_px_x, target_px_y = pygame.mouse.get_pos() 
            
            target_mm_x = robot.conversion_From_px_x_To_mm_x(target_px_x)
            target_mm_y = robot.conversion_From_px_y_To_mmy(target_px_y)
            print("target_mm_x: ", target_mm_x, "  target_mm_y: ", target_mm_y)
            #rotation_to_do_relatif, angle_objectif_absolue, distance = robot.calculate_target_angle_relatif_absolu_distance(target_mm_x, target_mm_y)
            target_angle = robot.calculate_target_angle(target_mm_x, target_mm_y)
            print("target angle after fonction calculate_target_angle: ", target_angle)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                try:
                    target_angle = int(angle_input) # Convertir en entier et limiter entre 0-359
                    distance_to_do = 10  # Distance fixe pour le mouvement
                    set_direction(target_angle)
                    print("input angle: ", target_angle)

                    if target_angle > 180:
                        print("erreur angle > 180")
                        pygame.quit()
                    angle_input = ""  # Réinitialiser la saisie

                except ValueError:
                    angle_input = ""  # Réinitialiser en cas d'erreur
            elif event.key == pygame.K_BACKSPACE:  # Effacer le dernier caractère
                angle_input = angle_input[:-1]
            elif event.unicode.isdigit() or (event.unicode == '-' and angle_input == ""):
                # Ajouter des chiffres ou un signe "-" au début
                angle_input += event.unicode

    #print("angle_diff:", angle_diff, "   robot.angle:", robot.angle, "   target_angle:", target_angle)

    angle_diff = normalize_angle(target_angle - robot.angle) 
    ###test###
    
    if   ( abs(angle_diff) >= 1 ):
        robot.angle += 1 * (1 if angle_diff > 0 else -1)
        robot.angle = normalize_angle(robot.angle)
        print("rotation // angle_diff:", angle_diff, "   robot.angle:", robot.angle)
    else:
        if robot.distance_to_target >=1 :
            robot.distance_to_target =robot.move_towards(robot.distance_to_target)
            #print("distance_to_do:",distance_to_do)
            #distance_to_do -= 1
            #robot.mm_x += dx
            #robot.mm_y += dy

        
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
    text_surface = font.render(f"Angle: {angle_input}", True, (255, 255, 255))
    screen.blit(text_surface, (screen.get_width() - text_surface.get_width() - 10, 10))

    pygame.display.flip() # peut-être pas besoin
    pygame.display.update()

pygame.quit()
