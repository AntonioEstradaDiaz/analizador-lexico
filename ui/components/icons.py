"""Iconos de navegación dibujados para distintas densidades de pantalla."""

from PIL import Image, ImageDraw
from customtkinter import CTkImage

from ui import theme as t


def navigation_icon(index: int, color: str = t.MUTED) -> CTkImage:
    """Dibuja iconos de trazo nítido para los cinco módulos."""
    image = Image.new("RGBA", (72, 72))
    draw = ImageDraw.Draw(image)

    def line(*points: tuple[int, int]) -> None:
        """Traza un segmento o una figura a cuatro veces la resolución final."""
        draw.line([(x * 4, y * 4) for x, y in points], fill=color, width=6,
                  joint="curve")

    def circle(x: int, y: int, radius: int) -> None:
        """Dibuja un contorno circular en la imagen de alta resolución."""
        draw.ellipse(((x - radius) * 4, (y - radius) * 4,
                      (x + radius) * 4, (y + radius) * 4), outline=color, width=6)

    if index == 0:
        line((6, 5), (2, 9), (6, 13))
        line((12, 5), (16, 9), (12, 13))
        line((10, 3), (8, 15))
    elif index == 1:
        circle(4, 9, 3)
        circle(14, 9, 3)
        line((7, 9), (11, 9))
    elif index == 2:
        line((4, 2), (15, 2), (15, 16), (4, 16), (4, 2))
        line((6, 9), (8, 11), (13, 6))
    elif index == 3:
        line((9, 5), (3, 3), (2, 3), (2, 14), (3, 14), (9, 16),
             (15, 14), (16, 14), (16, 3), (15, 3), (9, 5), (9, 16))
    else:
        circle(9, 9, 7)
        line((9, 8), (9, 13))
        line((9, 5), (9, 6))
    return CTkImage(light_image=image, dark_image=image, size=(18, 18))
