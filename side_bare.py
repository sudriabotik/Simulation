import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UILabel, UITextEntryLine, UIButton, UIHorizontalSlider
from setup import Screen_WIDTH, Screen_HEIGHT, FIELD_WIDTH, FIELD_HEIGHT

W, H = Screen_WIDTH, Screen_HEIGHT
UI_W = Screen_WIDTH - FIELD_WIDTH

def parse_number(s, default, integer=True):
    try:
        v = float(s.replace(',', '.'))
        return int(v) if integer else v
    except Exception:
        return default

def create_sidebar(manager,robot):
    ui_panel = UIPanel(relative_rect=pygame.Rect(W-UI_W, 0, UI_W, H), manager=manager)

    lbl_x = UILabel(relative_rect=pygame.Rect(10, 30, 80, 30), text="init_x_mm :", manager=manager, container=ui_panel)
    ent_x = UITextEntryLine(relative_rect=pygame.Rect(100, 30, UI_W-110, 30), manager=manager, container=ui_panel)
    ent_x.set_text(str(robot.mm_x))

    lbl_y = UILabel(relative_rect=pygame.Rect(10, 70, 80, 30), text="init_y_mm :", manager=manager, container=ui_panel)
    ent_y = UITextEntryLine(relative_rect=pygame.Rect(100, 70, UI_W-110, 30), manager=manager, container=ui_panel)
    ent_y.set_text(str(robot.mm_y))

    lbl_teta = UILabel(relative_rect=pygame.Rect(10, 110, 80, 30), text="init_teta :", manager=manager, container=ui_panel)
    ent_teta = UITextEntryLine(relative_rect=pygame.Rect(100, 110, UI_W-110, 30), manager=manager, container=ui_panel)
    ent_teta.set_text(str(robot.angle))

    lbl_file = UILabel(relative_rect=pygame.Rect(10, 150, 80, 30), text="strat file :", manager=manager, container=ui_panel)
    ent_file = UITextEntryLine(relative_rect=pygame.Rect(100, 150, UI_W-110, 30), manager=manager, container=ui_panel)
    ent_file.set_text("test_V2.txt")  # Valeur par défaut

    btn_apply = UIButton(relative_rect=pygame.Rect(10, 190, UI_W-20, 36), text="Appliquer", manager=manager, container=ui_panel)
    btn_start = UIButton(relative_rect=pygame.Rect(10, 240, UI_W-20, 36), text="Start", manager=manager, container=ui_panel)

    return ui_panel, lbl_x, ent_x, lbl_y, ent_y, lbl_teta, ent_teta, lbl_file, ent_file, btn_apply, btn_start
