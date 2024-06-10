from PIL import Image, ImageDraw, ImageFont
from customtkinter import CTkImage


def emoji_to_ctk_img(text, size=24, font="seguiemj.ttf"):
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    font = ImageFont.truetype(font, size=int(round(size*72/96, 0)))
    draw = ImageDraw.Draw(img)
    draw.text(
        (size/2, size/2), text, embedded_color=True, font=font, anchor="mm")

    return CTkImage(img, size=(size, size))
