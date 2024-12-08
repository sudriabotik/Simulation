from setup import TABLE_WIDTH_MM, TABLE_HEIGHT_MM, Screen_WIDTH, Screen_HEIGHT

def conversion_From_mmx_To_px_x(mm_x):
    px_x = ((TABLE_WIDTH_MM - mm_x) /TABLE_WIDTH_MM)*Screen_WIDTH
    return px_x
    
def conversion_From_mmy_To_px_y(mm_y):
    px_y = ((TABLE_HEIGHT_MM - mm_y)/TABLE_HEIGHT_MM)*Screen_HEIGHT
    return px_y

def conversion_From_px_x_To_mm_x(px_x):
    x_mm = (Screen_WIDTH - px_x) * (TABLE_WIDTH_MM / Screen_WIDTH)
    return x_mm

def conversion_From_px_y_To_mmy(px_y):
    y_mm = (Screen_HEIGHT - px_y) * (TABLE_HEIGHT_MM / Screen_HEIGHT)
    return y_mm


# purpose ?
def conversion_trigo_transform_rotate(angle):
        angle_px = (angle-90)
        return angle_px
    
def normalize_angle(angle):
    angle = angle % 360  
    if angle > 180:
        angle -= 360  
    return angle