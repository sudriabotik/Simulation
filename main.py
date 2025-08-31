import pygame
from side_bare import create_sidebar, parse_number, UI_W
import pygame_gui
from robot import Robot, FPS, create_robot_surface
from setup import init,Screen_WIDTH, Screen_HEIGHT
from read_strat_file import strategie, parse_fdd_commands
from rec_strat import write_rejoindre_command, write_orienter_command, create_txt_file, display_mouse_coords
file_strat_path = 'test.txt'
file_rec_path = 'rec.txt'

''' 
to do : 
Les prochaines updates c’est :
- Rajouter les bouton orientation et rejoindre pour choisir la fonction que l’on veut faire. 
- Les boutons de la face et de la vitesse pour pouvoir custom chaque mouvement. 
- ⁠le temps d’une strate
- Les points remarcable
- pouvoir mettre en pause une strate
- pouvoir completer une strate deja commencer 
'''  
face_robot = 0
vitesse_robot = 100
fonction_robot = "rejoindre"  # "rejoindre" ou "orienter"
enregistrement = False
commands = None
start_strat = False 
stop_strat = False
pause_strat = False
running = True
strategy_start_time = 0
mouse_mm_x_valid, mouse_mm_y_valid = 0,0

screen, scaled_vinyle, manager = init()
clock = pygame.time.Clock()  # Horloge pour gérer le temps

image_robot, rect_robot = create_robot_surface()

robot = Robot(scaled_vinyle, screen, image_robot)

(ui_panel, lbl_init, ent_x, ent_y, ent_o, lbl_x, lbl_y, lbl_o,
        lbl_speed, ent_max_speed, ent_accel, ent_max_turning_speed, ent_turning_accel,
        lbl_max_speed, lbl_accel, lbl_max_turning_speed, lbl_turning_accel,
        lbl_file, ent_file, btn_apply, btn_start, btn_enregistrer,
        lbl_rec_file, ent_rec_file, btn_valid, lbl_mouse_coords, lbl_mouse_mm_valid,
        btn_stop, btn_pause, btn_face, btn_vitesse, btn_fonction) = create_sidebar(manager, robot, enregistrement)

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
                strategy_start_time = pygame.time.get_ticks() / 1000.0  # Temps en secondes
                print("Start strategy execution...")
            
            if event.ui_element == btn_enregistrer:
                enregistrement = not enregistrement
                if enregistrement:
                    file_rec_path = ent_rec_file.get_text()
                    btn_enregistrer.set_text('Enregistrement ON')
                    file_rec_path = create_txt_file(file_rec_path)  # Récupérer le chemin complet
                else:
                    btn_enregistrer.set_text('Enregistrement OFF')

            if event.ui_element == btn_valid:
                if fonction_robot == "rejoindre":
                    write_rejoindre_command(mouse_mm_x_valid, mouse_mm_y_valid, file_rec_path, str(face_robot), str(vitesse_robot))
                    robot.rejoindre(mouse_mm_x_valid, mouse_mm_y_valid, face_robot, vitesse_robot)
                elif fonction_robot == "orienter":
                    write_orienter_command(robot.angle, file_rec_path, str(vitesse_robot))
                    # Pour orienter, on peut utiliser l'angle actuel du robot ou calculer l'angle vers la souris
                    target_angle = robot.calculate_target_angle(mouse_mm_x_valid, mouse_mm_y_valid)
                    robot.orienter(target_angle, vitesse_robot)
            
            if event.ui_element == btn_stop:
                start_strat = False
                stop_strat = True
                pause_strat = False
                commands = None
                strategy_start_time = 0
                print("Strategy stopped")
            
            if event.ui_element == btn_pause:
                if pause_strat:
                    pause_strat = False
                    btn_pause.set_text("Pause")
                    print("Strategy resumed")
                else:
                    pause_strat = True
                    btn_pause.set_text("Resume")
                    print("Strategy paused")
            
            if event.ui_element == btn_face:
                face_robot = 1 - face_robot  # Toggle entre 0 et 1
                btn_face.set_text(f"Face: {face_robot}")
                print(f"Face changed to: {face_robot}")
            
            if event.ui_element == btn_vitesse:
                # Cycle entre 25%, 50%, 75%, 100%
                vitesse_options = [25, 50, 75, 100]
                current_index = vitesse_options.index(vitesse_robot) if vitesse_robot in vitesse_options else 3
                next_index = (current_index + 1) % len(vitesse_options)
                vitesse_robot = vitesse_options[next_index]
                btn_vitesse.set_text(f"Vitesse: {vitesse_robot}%")
                print(f"Speed changed to: {vitesse_robot}%")
            
            if event.ui_element == btn_fonction:
                if fonction_robot == "rejoindre":
                    fonction_robot = "orienter"
                    btn_fonction.set_text("Fonction: Orienter")
                    print("Function changed to: orienter")
                else:
                    fonction_robot = "rejoindre"
                    btn_fonction.set_text("Fonction: Rejoindre")
                    print("Function changed to: rejoindre")

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

    # Mise à jour du chronomètre
    current_time = pygame.time.get_ticks() / 1000.0  # Temps en secondes
    if robot.graphique:
        robot.graphique.update_strategy_time(current_time if strategy_start_time > 0 else 0, start_strat and not pause_strat)
    
    if not pause_strat:
        strategie(robot, start_strat, commands)
    #print("mouse_mm_x_valid: ",mouse_mm_x_valid, "mouse_mm_y_valid: ",mouse_mm_y_valid,"mouse_mm_x: ",mouse_mm_x,"mouse_mm_y: ",mouse_mm_y)
    robot.graphique.refesh_graphique()

pygame.quit()
