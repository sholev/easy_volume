import customtkinter as ctk


# Avoid setting of the default icon
class CTkToplevel(ctk.CTkToplevel):

    def __init__(self, *args, fg_color=None, **kwargs):
        self.iconbitmap = self.wm_iconbitmap
        super().__init__(*args, fg_color=fg_color, **kwargs)

    def wm_iconbitmap(self, bitmap=None, default=None):
        pass

    def reload(self):
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


class CTkVisibilityGridFrame(ctk.CTkFrame):
    def __init__(self, master,  **kwargs):
        super().__init__(master, **kwargs)
        self.is_visible = True

    def set_visibility(self, is_visible: bool):
        self.is_visible = is_visible
        if is_visible:
            self.grid()
        else:
            self.grid_remove()
