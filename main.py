import pygame
from side_bare import create_sidebar, parse_number, UI_W
import pygame_gui
from robot import Robot, FPS, create_robot_surface
from setup import init,Screen_WIDTH, Screen_HEIGHT
from read_strat_file import strategie, parse_fdd_commands

file_strat_path = 'test_V2.txt'

screen, scaled_vinyle, manager = init()
clock = pygame.time.Clock()  # Horloge pour gérer le temps

image_robot, rect_robot = create_robot_surface()

robot = Robot(scaled_vinyle, screen, image_robot)

ui_panel, lbl_x, ent_x, lbl_y, ent_y, lbl_teta, ent_teta, lbl_file, ent_file, btn_apply, btn_start = create_sidebar(manager, robot)

commands = None
start_strat = False 
running = True

while running:
    dt = clock.tick(FPS) / 1000  # Limite à 60 FPS et conversion en secondes

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        manager.process_events(event)

        # Bouton "Appliquer" -> relire toutes les valeurs d’un coup (optionnel)
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == btn_apply:
            robot.mm_x = parse_number(ent_x.get_text(), robot.mm_x)
            robot.mm_y = parse_number(ent_y.get_text(), robot.mm_y)
            robot.angle = parse_number(ent_teta.get_text(), robot.angle)
            print("bouton appliquer pressed")

        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == btn_start:
            try:
                commands = parse_fdd_commands(file_strat_path)
                print("commands init_____: ", commands)
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier de stratégie : {e}")
            start_strat = True
            print("Start strategy execution...")

        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == ent_x:
                robot.mm_x = parse_number(event.text, robot.mm_x)
                ent_x.set_text(str(robot.mm_x))
            elif event.ui_element == ent_y:
                robot.mm_y = parse_number(event.text, robot.mm_y)
                ent_y.set_text(str(robot.mm_y))
            elif event.ui_element == ent_teta:
                robot.angle = parse_number(event.text, robot.angle)
                ent_teta.set_text(str(robot.angle))
            elif event.ui_element == ent_file:
                file_strat_path = event.text
                ent_file.set_text(file_strat_path)
                

    pygame.draw.rect(screen, (60, 60, 60), pygame.Rect(0, 0, Screen_WIDTH - UI_W, Screen_HEIGHT))  # ta scène 900 px
    manager.update(dt)
    manager.draw_ui(screen)

    print("file_strat_path: ", file_strat_path, "  start_strat: ", start_strat)
    strategie(robot, start_strat, commands)

    robot.graphique.refesh_graphique()

pygame.quit()
