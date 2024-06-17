import os
import sys
from PIL import Image, ImageDraw, ImageFont
from customtkinter import CTkImage


def emoji_to_ctk_img(text, size=24, font="seguiemj.ttf"):
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    font = ImageFont.truetype(font, size=int(round(size*72/96, 0)))
    draw = ImageDraw.Draw(img)
    draw.text(
        (size/2, size/2), text, embedded_color=True, font=font, anchor="mm")

    return CTkImage(img, size=(size, size))


def get_path(file):
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS')
    elif 'Nuitka' in sys.modules:
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, file)
