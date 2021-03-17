# File with program constants

WIDTH = 1280
HEIGHT = 720

WIDTH_FRAME_DATA = WIDTH * (1 / 5)
WIDTH_FRAME_OPT = 1036 #WIDTH * (4 / 5) #1024
WIDTH_FRAME_IMG = 1024 #WIDTH * (4 / 5) #1024

HEIGHT_FRAME_DATA = HEIGHT
HEIGHT_FRAME_OPT = HEIGHT * (1 / 7) #102.857
HEIGHT_FRAME_IMG = 610 #HEIGHT * (6 / 7) #617.1428

# Initial Upload Frame
WIDTH_UI_FD_TXT_INICIAL = WIDTH_FRAME_DATA / 2
HEIGHT_UI_FD_TXT_INICIAL = 50

WIDTH_UI_FD_BT_REST = WIDTH_FRAME_DATA / 2
HEIGHT_UI_FD_BT_REST = 100
WIDTH_UI_FD_BT_STRESS = WIDTH_FRAME_DATA / 2
HEIGHT_UI_FD_BT_STRESS = 150

WIDTH_UI_BT_PROCESS = WIDTH_FRAME_OPT / 2
HEIGHT_UI_BT_PROCESS = HEIGHT_FRAME_OPT / 2

BORDER_UI_IMG = 2
WIDTH_UI_RESULT = WIDTH_FRAME_IMG
WIDTH_UI_RES_IMG = WIDTH_UI_RESULT / 2
WIDTH_UI_RES_IMG_REST = WIDTH_UI_RES_IMG
WIDTH_UI_RES_IMG_STRESS = WIDTH_UI_RES_IMG
HEIGHT_UI_RESULT = HEIGHT_FRAME_IMG

WIDTH_TEXT_TITLE_IMG = WIDTH_UI_RES_IMG_REST
HEIGHT_TEXT_TITLE_IMG = 20
HEIGHT_CANVAS_IMG = HEIGHT_UI_RESULT - HEIGHT_TEXT_TITLE_IMG

#  Preview images on Upload_Image
WIDTH_CANVAS_IMG_UL = WIDTH_UI_RES_IMG
WIDTH_IMG_UL = WIDTH_UI_RESULT / 4


####  SCREEN RESULTS  #####

WIDTH_FRAME_BUTTONS = int(WIDTH_FRAME_OPT / 3)
WIDTH_BUTTONS_OPT = int(WIDTH_FRAME_BUTTONS/2)
HEIGHT_FRAME_BUTTONS = int(HEIGHT_FRAME_OPT)
HEIGHT_BUTTONS_OPT = int(HEIGHT_FRAME_BUTTONS/3)
pos_x_buttons_opt = int(WIDTH_FRAME_BUTTONS/2)
pos_y_buttons_opt = int(HEIGHT_FRAME_BUTTONS/2)

width_res_opt_title = 250 #original width_res_opt_title = 240
height_res_opt_title = 60 #original height_res_opt_title = 40
height_res_opt_paciente = 30
height_res_opt_study = 30
height_res_opt_series_id = 30
height_res_opt_series_desc = 30

height_res_opt_espacio = 20

height_res_opt_curva_title = 30
height_res_opt_curva_button = 30
width_res_opt_curva_button = 80
height_res_opt_curva_grafico = 150


height_img_res_screen = 306
width_img_res_screen = 306
h_mid_img = height_img_res_screen/2
w_mid_img = width_img_res_screen/2

width_title_img = 306
height_title_img = 40

width_button_init_fin = 40
height_button_init_fin = 30

width_button_left_right = 30
height_button_left_right = 30
width_label_info_res = 196
height_label_info_res = 30

width_label_valor_img = 60
height_label_valor_img = 30
width_valor_img = 120
height_valor_img = 30

w_espacio_1 = 50
h_espacio_1 = HEIGHT_FRAME_IMG
w_espacio_2 = 50
h_espacio_2 = HEIGHT_FRAME_IMG
w_espacio_3 = 70
h_espacio_3 = HEIGHT_FRAME_IMG
w_espacio_4 = 42
h_espacio_4 = HEIGHT_FRAME_IMG

w_dif_1 = width_title_img
h_dif_1 = 15
w_dif_2 = width_title_img
h_dif_2 = 10
w_dif_3 = width_title_img
h_dif_3 = 10
w_dif_4 = 116
h_dif_4 = 30
w_dif_5 = width_title_img
h_dif_5 = 135

w_dif_7 = 80
h_dif_7 = 53
w_dif_8 = 80
h_dif_8 = 43
w_dif_9 = 80
h_dif_9 = 30


