import customtkinter as ctk

from customtkinter.windows.widgets.core_widget_classes import DropdownMenu

from utils import emoji_to_ctk_img


# Avoid setting of the default icon
class CTkToplevel(ctk.CTkToplevel):

    def __init__(self, *args, fg_color=None, **kwargs):
        self.iconbitmap = self.wm_iconbitmap
        super().__init__(*args, fg_color=fg_color, **kwargs)

    def wm_iconbitmap(self, bitmap=None, default=None):
        pass

    def reload(self):
        pass

    def refresh(self):
        pass


class ToggleVisibilityWindow:
    def __init__(self, window: CTkToplevel, minimized: bool = True):
        self.window = window
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        self.is_visible = not minimized
        if minimized:
            self.hide()

    def show(self):
        self.window.deiconify()
        self.is_visible = True

    def hide(self):
        self.window.withdraw()
        self.is_visible = False

    def toggle(self):
        if self.is_visible:
            self.hide()
        else:
            self.show()

    def reload(self):
        self.window.reload()

    def refresh(self):
        self.window.refresh()


class CTkVisibilityGridFrame(ctk.CTkFrame):
    def __init__(self, master,  **kwargs):
        super().__init__(master, **kwargs)
        self.is_visible = True

    def set_visibility(self, is_visible: bool):
        self.is_visible = is_visible
        if is_visible:
            self.grid()
            self.refresh()
        else:
            self.grid_remove()

    def refresh(self):
        pass


class CustomDropdown(ctk.CTkFrame):
    def __init__(self, parent, values, command=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.values = values
        self.command = command

        self.dropdown_button = ctk.CTkButton(
            self, text='', image=emoji_to_ctk_img("⇅"), width=20,
            command=self.show_menu
        )
        self.dropdown_button.pack()

        self.dropdown_menu = DropdownMenu(self, values=values, command=command)

    def show_menu(self):
        self.update_idletasks()
        x = self.dropdown_button.winfo_rootx()
        y = (self.dropdown_button.winfo_rooty() +
             self.dropdown_button.winfo_height())
        self.dropdown_menu.open(x, y)

    def select_option(self, option):
        if self.command:
            self.command(option)
