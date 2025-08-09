import pygame

# Constants for the table size in mm and image path
TABLE_WIDTH_MM = 3000
TABLE_HEIGHT_MM = 2000
IMAGE_PATH = 'botikplaymat.jpg'  # Update this to your image path

# Screen setup
#il faut respecter la prortion 3/2 pour l'image du terrain
Screen_WIDTH, Screen_HEIGHT = 1200, 600
FIELD_WIDTH, FIELD_HEIGHT = 900,600 
def init_pygame():
    pygame.init()
    screen = pygame.display.set_mode((Screen_WIDTH, Screen_HEIGHT))
    return screen

def load_image():
    image = pygame.image.load(IMAGE_PATH)
    img_width, img_height = image.get_size()
    return image, img_width, img_height