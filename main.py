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
mouse_mm_x_valid, mouse_mm_y_valid = 0,0

screen, scaled_vinyle, manager = init()
clock = pygame.time.Clock()  # Horloge pour gérer le temps

image_robot, rect_robot = create_robot_surface()

robot = Robot(scaled_vinyle, screen, image_robot)

(ui_panel, lbl_init, ent_x, ent_y, ent_o, lbl_x, lbl_y, lbl_o,
        lbl_speed, ent_max_speed, ent_accel, ent_max_turning_speed, ent_turning_accel,
        lbl_max_speed, lbl_accel, lbl_max_turning_speed, lbl_turning_accel,
        lbl_file, ent_file, btn_apply, btn_start, btn_enregistrer,
        lbl_rec_file, ent_rec_file, btn_valid, lbl_mouse_coords,lbl_mouse_mm_valid) = create_sidebar(manager, robot, enregistrement)

while running:
    dt = clock.tick(FPS) / 1000  # Limite à 60 FPS et conversion en secondes

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        manager.process_events(event)

        target_px_x, target_px_y = pygame.mouse.get_pos() 
        mouse_mm_x = int ( robot.conversion_From_px_x_To_mm_x(target_px_x))
        mouse_mm_y = int ( robot.conversion_From_px_y_To_mmy(target_px_y))
        lbl_mouse_coords.set_text(f"Souris terrain: X={mouse_mm_x} mm, Y={mouse_mm_y} mm")

        # Bouton "Appliquer" -> relire toutes les valeurs d’un coup (optionnel)
        if event.type == pygame_gui.UI_BUTTON_PRESSED :
            if event.ui_element == btn_apply:
                robot.mm_x = parse_number(ent_x.get_text(), robot.mm_x)
                robot.mm_y = parse_number(ent_y.get_text(), robot.mm_y)
                robot.angle = parse_number(ent_o.get_text(), robot.angle)
                file_strat_path = ent_file.get_text()
                robot.max_speed = parse_number(ent_max_speed.get_text(), robot.max_speed)
                robot.acceleration = parse_number(ent_accel.get_text(), robot.acceleration)
                robot.max_turning_speed = parse_number(ent_max_turning_speed.get_text(), robot.max_turning_speed)
                robot.turning_acceleration = parse_number(ent_turning_accel.get_text(), robot.turning_acceleration)
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

            if event.ui_element == btn_valid:
                write_rejoindre_command(mouse_mm_x_valid, mouse_mm_y_valid, file_rec_path)
                robot.rejoindre(mouse_mm_x_valid, mouse_mm_y_valid, 0, 100)

        if (enregistrement == True) :
            lbl_mouse_mm_valid.set_text(f"value____: X={mouse_mm_x_valid} mm, Y={mouse_mm_y_valid} mm")
            if (event.type == pygame.MOUSEBUTTONDOWN) and (mouse_mm_x > 0):
                mouse_mm_x_valid = mouse_mm_x
                mouse_mm_y_valid = mouse_mm_y
                #lbl_mouse_mm_valid.set_text(f"value____: X={mouse_mm_x_valid} mm, Y={mouse_mm_y_valid} mm")  
        else:
            #lbl_mouse_coords.set_text("")
            lbl_mouse_mm_valid.set_text("")

        if ( (enregistrement == False) and (start_strat == False) and (event.type == pygame.MOUSEBUTTONDOWN) and (mouse_mm_x > 0)):
            robot.rejoindre(mouse_mm_x, mouse_mm_y, 0, 100)

    pygame.draw.rect(screen, (60, 60, 60), pygame.Rect(0, 0, Screen_WIDTH - UI_W, Screen_HEIGHT))  # ta scène 900 px
    manager.update(dt)
    manager.draw_ui(screen)

    strategie(robot, start_strat, commands)
    print("mouse_mm_x_valid: ",mouse_mm_x_valid, "mouse_mm_y_valid: ",mouse_mm_y_valid,"mouse_mm_x: ",mouse_mm_x,"mouse_mm_y: ",mouse_mm_y)
    robot.graphique.refesh_graphique()

pygame.quit()
