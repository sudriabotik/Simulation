import os
import pygame

def create_txt_file(filename):
    if not filename.endswith('.txt'):
        filename += '.txt'
    with open(filename, 'w') as f:
        pass  # Crée un fichier vide
    return filename

def write_rejoindre_command(target_mm_x, target_mm_y, filename, face="0", ratio_vitesse="100", ser="ser"):

    if target_mm_x < 0 :
        return None

    # Formatage des coordonnées sur 4 chiffres avec des zéros devant
    x_str = f"{int(target_mm_x):04d}"
    y_str = f"{int(target_mm_y):04d}"
    # Construction de la ligne au format attendu
    line = f'fdd.rejoindre("{x_str}", "{y_str}", "{face}", "{ratio_vitesse}", {ser})\n'
    # Écriture dans le fichier
    with open(filename, 'a') as f:
        f.write(line)

def display_mouse_coords(screen, mouse_mm_x, mouse_mm_y, Screen_HEIGHT, font_size=15, color=(255, 255, 0)):
    font = pygame.font.Font(None, font_size)
    mouse_text = font.render(f"Souris terrain: X={mouse_mm_x} mm, Y={mouse_mm_y} mm", True, color)
    screen.blit(mouse_text, (910, Screen_HEIGHT - 30))

