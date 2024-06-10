import os
from tkinter import PhotoImage
from PIL import Image
from customtkinter import set_appearance_mode, set_default_color_theme

from tray_app import TrayApp
from audio_devices_window import AudioDevicesWindow
from about_window import AboutWindow
from startup_manager import StartupManager
from config import config
from version import VERSION


POS_OFFSET_X = 20
POS_OFFSET_Y = POS_OFFSET_X * 5

APP_NAME = 'Easy Volume'
ICON_PATH = os.path.join(os.path.dirname(__file__), 'resources/icon.png')


def init_audio_devices_window(root, width=450, height=500):
    window = AudioDevicesWindow(root)
    window.iconphoto(False, PhotoImage(file=ICON_PATH))
    window.minsize(width, height)
    pos_x = root.winfo_screenwidth() - width - POS_OFFSET_X
    pos_y = root.winfo_screenheight() - height - POS_OFFSET_Y
    size = f'{width}x{height}'
    pos = f'+{pos_x}+{pos_y}'
    window.geometry(geometry_string=f'{size}+{pos}')

    return window


def init_about_window(root, width=300, height=150):
    about_window = AboutWindow(root, VERSION)
    about_window.iconphoto(False, PhotoImage(file=ICON_PATH))
    about_window.resizable(False, False)
    pos_x = about_window.winfo_screenwidth() - width - POS_OFFSET_X
    pos_y = about_window.winfo_screenheight() - height - POS_OFFSET_Y
    pos = f'+{pos_x}+{pos_y}'
    size = f'{width}x{height}'
    about_window.geometry(geometry_string=f'{size}+{pos}')

    return about_window


if __name__ == "__main__":
    set_default_color_theme(config.get('theme'))
    set_appearance_mode(config.get('appearance'))

    startup_manager = StartupManager(APP_NAME, __file__)
    app = TrayApp(APP_NAME, Image.open(ICON_PATH), config, startup_manager)

    app.add_window(
        "Audio Devices",
        init_audio_devices_window(app.root),
        config.get('start_minimized')
    )

    app.add_window(
        "About",
        init_about_window(app.root),
        start_minimized=True
    )

    app.mainloop()
