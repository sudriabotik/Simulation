import pygame
from robot import Robot
from setup import init_pygame, TABLE_WIDTH_MM, TABLE_HEIGHT_MM, Screen_WIDTH, Screen_HEIGHT

screen = init_pygame()

robot = Robot()
robot_rectangle = pygame.Rect(robot.px_x, robot.px_y, robot.px_width, robot.px_height)

### debug###
font = pygame.font.Font(None, 36)
target_mm_x = 0
target_mm_y = 0
####debug_fin###

running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            target_px_x, target_px_y = pygame.mouse.get_pos() 
            
            target_mm_x = (Screen_WIDTH - target_px_x) * (TABLE_WIDTH_MM / Screen_WIDTH) #target_px_x = Screen_WIDTH - target_px_x # symétrie car par default le point d'origine est en bas à gauche
            target_mm_y = (Screen_HEIGHT - target_px_y) * (TABLE_HEIGHT_MM / Screen_HEIGHT)
            ###test###
            robot.x = target_mm_x
            robot.y = target_mm_y
            robot_rectangle.center = (target_px_x, target_px_y)
            ###test fin###

    pygame.draw.rect(screen, (255, 0, 0), robot_rectangle)

    ##debug##
    coords_text = font.render(f"X: {int(target_mm_x)} mm, Y: {int(target_mm_y)} mm", True, (255, 255, 255))
    screen.blit(coords_text, (10, 10))  # Position du texte en haut à gauche
    ##debug_fin##

    pygame.display.flip()

pygame.quit()