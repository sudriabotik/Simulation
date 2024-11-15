import pygame

# Constants for the table size in mm and image path
TABLE_WIDTH_MM = 3000
TABLE_HEIGHT_MM = 2000
IMAGE_PATH = 'map_cfdr_2025.png'  # Update this to your image path

# Screen setup
Screen_WIDTH, Screen_HEIGHT = 900, 600

def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((Screen_WIDTH, Screen_HEIGHT))
    return screen

def load_image():
    image = pygame.image.load(IMAGE_PATH)
    img_width, img_height = image.get_size()
    return image, img_width, img_height
