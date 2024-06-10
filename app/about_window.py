import customtkinter as ctk
import customtkinter_extensions as ctk_e
import webbrowser


FONT = "Arial"
TITLE = "Easy Volume"
LINK = "https://github.com/sholev/easy_volume"


class AboutWindow(ctk_e.CTkToplevel):
    def __init__(self, parent, version, title='About', geometry='300x150'):
        super().__init__(parent)

        self.title(title)
        self.geometry(geometry)

        self.label_name = ctk.CTkLabel(self, text=TITLE, font=(FONT, 16))
        self.label_name.pack(pady=10)

        self.label_version = ctk.CTkLabel(self, text=version, font=(FONT, 14))
        self.label_version.pack(pady=5)

        self.label_link = ctk.CTkLabel(
            self, text=LINK, text_color=('blue', 'skyblue'),
            font=(FONT, 14, 'underline'), cursor="hand2"
        )
        self.label_link.pack(pady=10)
        self.label_link.bind(
            "<Button-1>",
            lambda _: webbrowser.open(LINK)
        )


if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("400x300")
    about_window = AboutWindow(root, "v0.1.0")
    about_window.grab_set()
    root.mainloop()
