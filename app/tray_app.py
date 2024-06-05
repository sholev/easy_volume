import os
import importlib.util
from functools import partial
from pystray import Icon, Menu, MenuItem as Item
from customtkinter import CTk, set_appearance_mode, set_default_color_theme

from customtkinter_extensions import ToggleVisibilityWindow, CTkToplevel
from startup_manager import StartupManager
from config import Config

APPEARANCES = ['system', 'dark', 'light']


class TrayApp:
    def __init__(self, title, icon_image,
                 config: Config,
                 startup_manager: StartupManager):
        self.root = CTk()
        self.root.withdraw()
        self.windows = {}
        self.config = config
        self.startup_manager = startup_manager
        self.icon = self.get_icon(title, icon_image)

    def mainloop(self):
        self.root.mainloop()

    def add_window(self, title, window: CTkToplevel, start_minimized=False):
        self.windows[title] = ToggleVisibilityWindow(window, start_minimized)
        self.update_menu(self.icon)

    def get_icon(self, title, icon_image):
        icon = Icon("name", icon_image, title)
        icon.run_detached()
        self.update_menu(icon)

        return icon

    def update_menu(self, icon: Icon):
        icon.menu = Menu(*self.get_main_menu())

    def get_main_menu(self):
        menu = []
        is_default = True
        for name, window in self.windows.items():
            action = partial(self.toggle_window, window)
            menu.append(Item(text=name, action=action, default=is_default))
            is_default = False

        menu.extend([
            Item(text='Appearance', action=Menu(*self.get_appearance_menu())),
            Item(text='Settings', action=Menu(*self.get_settings_menu())),
            Item(text='Quit', action=self.quit_app)
        ])

        return menu

    def get_appearance_menu(self):
        menu = []

        def is_appearance_selected(appearance_item):
            return appearance_item.text == self.config.get('appearance')

        def set_appearance(appearance_name, *_):
            set_appearance_mode(appearance_name)
            self.config.set('appearance', appearance_name)

        menu.append(Item(text='Appearance:', action=None, enabled=False))
        for appearance in APPEARANCES:
            menu.append(Item(text=appearance,
                             action=partial(set_appearance, appearance),
                             checked=is_appearance_selected))

        def get_theme_names():
            ctk_spec = importlib.util.find_spec("customtkinter")
            ctk_path = os.path.dirname(ctk_spec.origin)
            themes_dir = os.path.join(ctk_path, 'assets/themes')
            files = [t for t in os.listdir(themes_dir) if t.endswith('.json')]
            return [t.replace('.json', '') for t in files]

        def is_theme_selected(theme_item):
            return theme_item.text == self.config.get('theme')

        def set_theme(theme_name, *_):
            set_default_color_theme(theme_name)
            self.config.set('theme', theme_name)
            for w in self.windows.values():
                w.reload()

        themes = get_theme_names()
        if themes is not None and len(themes) > 0:
            menu.append(Menu.SEPARATOR)
            menu.append(Item(text='Theme:', action=None, enabled=False))
            for theme in themes:
                menu.append(Item(text=theme,
                                 action=partial(set_theme, theme),
                                 checked=is_theme_selected))

        return menu

    def get_settings_menu(self):
        menu = []

        def is_start_minimized_enabled(*_):
            return self.config.get('start_minimized')

        def toggle_start_minimized(_: Icon):
            minimized = self.config.get('start_minimized')
            self.config.set('start_minimized', not minimized)

        menu.append(Item(text='Start minimized',
                         action=toggle_start_minimized,
                         checked=is_start_minimized_enabled))

        def is_start_on_logon_enabled(*_):
            return self.startup_manager.is_startup_enabled()

        def toggle_start_on_logon(_: Icon):
            if self.startup_manager.is_startup_enabled():
                self.startup_manager.disable_startup()
            else:
                self.startup_manager.enable_startup()

        menu.append(Item(text='Start on logon',
                         action=toggle_start_on_logon,
                         checked=is_start_on_logon_enabled))

        return menu

    def toggle_window(self, window, *_):
        self.root.after(0, window.toggle)

    def quit_app(self, _: Icon):
        self.icon.stop()
        self.root.quit()
