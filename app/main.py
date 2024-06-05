import os
from tkinter import PhotoImage
from PIL import Image
from customtkinter import set_appearance_mode, set_default_color_theme

from tray_app import TrayApp
from audio_devices_window import AudioDevicesWindow
from startup_manager import StartupManager
from config import config

WIDTH = 450
HEIGHT = 500
POS_OFFSET_X = 20
POS_OFFSET_Y = POS_OFFSET_X * 5

APP_NAME = 'Easy Volume'
ICON_PATH = os.path.join(os.path.dirname(__file__), 'resources/icon.png')


if __name__ == "__main__":
    set_default_color_theme(config.get('theme'))
    set_appearance_mode(config.get('appearance'))

    startup_manager = StartupManager(APP_NAME, __file__)
    app = TrayApp(APP_NAME, Image.open(ICON_PATH), config, startup_manager)

    window = AudioDevicesWindow(app.root)
    window.iconphoto(False, PhotoImage(file=ICON_PATH))
    window.minsize(WIDTH, HEIGHT)

    pos_x = app.root.winfo_screenwidth() - WIDTH - POS_OFFSET_X
    pos_y = app.root.winfo_screenheight() - HEIGHT - POS_OFFSET_Y
    size = f'{WIDTH}x{HEIGHT}'
    pos = f'+{pos_x}+{pos_y}'
    window.geometry(geometry_string=f'{size}+{pos}')

    app.add_window("Audio Devices", window, config.get('start_minimized'))
    app.mainloop()
