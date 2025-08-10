import pygame
from side_bare import create_sidebar, parse_number, UI_W
import pygame_gui
from robot import Robot, FPS, create_robot_surface
from setup import init,Screen_WIDTH, Screen_HEIGHT
from read_strat_file import strategie, parse_fdd_commands
from rec_strat import write_rejoindre_command, create_txt_file, display_mouse_coords
file_strat_path = 'test_V2.txt'
file_rec_path = 'rec.txt'

enregistrement = False
commands = None
start_strat = False 
running = True

screen, scaled_vinyle, manager = init()
clock = pygame.time.Clock()  # Horloge pour gérer le temps

image_robot, rect_robot = create_robot_surface()

robot = Robot(scaled_vinyle, screen, image_robot)

(ui_panel, lbl_x, ent_x, lbl_y, ent_y, lbl_teta, ent_teta, lbl_file, ent_file,
            btn_apply, btn_start, btn_enregistrer, lbl_rec_file, ent_rec_file, btn_valid, lbl_mouse_coords) = create_sidebar(manager, robot, enregistrement)

while running:
    dt = clock.tick(FPS) / 1000  # Limite à 60 FPS et conversion en secondes

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        manager.process_events(event)

        # Bouton "Appliquer" -> relire toutes les valeurs d’un coup (optionnel)
        if event.type == pygame_gui.UI_BUTTON_PRESSED :
            if event.ui_element == btn_apply:
                robot.mm_x = parse_number(ent_x.get_text(), robot.mm_x)
                robot.mm_y = parse_number(ent_y.get_text(), robot.mm_y)
                robot.angle = parse_number(ent_teta.get_text(), robot.angle)
                file_strat_path = ent_file.get_text()
                print("bouton appliquer pressed")

            if  event.ui_element == btn_start:
                try:
                    commands = parse_fdd_commands(file_strat_path)
                    print("commands init_____: ", commands)
                except Exception as e:
                    print(f"Erreur lors de la lecture du fichier de stratégie : {e}")
                start_strat = True
                print("Start strategy execution...")
            
            if event.ui_element == btn_enregistrer:
                enregistrement = not enregistrement
                if enregistrement:
                    btn_enregistrer.set_text('Enregistrement ON')
                    create_txt_file(file_rec_path)
                else:
                    btn_enregistrer.set_text('Enregistrement OFF')


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
            elif event.ui_element == ent_rec_file:
                file_rec_path = event.text
                ent_rec_file.set_text(file_rec_path)

        if enregistrement == True:
            target_px_x, target_px_y = pygame.mouse.get_pos() 
            mouse_mm_x = int ( robot.conversion_From_px_x_To_mm_x(target_px_x))
            mouse_mm_y = int ( robot.conversion_From_px_y_To_mmy(target_px_y))
            lbl_mouse_coords.set_text(f"Souris terrain: X={mouse_mm_x} mm, Y={mouse_mm_y} mm")
            if (event.type == pygame.MOUSEBUTTONDOWN):
                write_rejoindre_command(mouse_mm_x, mouse_mm_y, file_rec_path)
        else:
            lbl_mouse_coords.set_text("")
                

    pygame.draw.rect(screen, (60, 60, 60), pygame.Rect(0, 0, Screen_WIDTH - UI_W, Screen_HEIGHT))  # ta scène 900 px
    manager.update(dt)
    manager.draw_ui(screen)

    strategie(robot, start_strat, commands)

    robot.graphique.refesh_graphique()

pygame.quit()
