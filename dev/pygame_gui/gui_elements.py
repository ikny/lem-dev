import pygame as pg
import sys


class Widget():
    def __init__(self, screen: pg.Surface, height: float = 0, width: float = 0, x: float = 0, y: float = 0) -> None:
        self.screen = screen
        self.height = height
        self.width = width
        self.x = x
        self.y = y


class Text(Widget):
    def __init__(self, screen: pg.Surface, text: str, height: float = 0, width: float = 0, x: float = 0, y: float = 0) -> None:
        super().__init__(screen, height, width, x, y)
        self.text = text

    def draw(self) -> None:
        font = pg.font.Font(None, size=36)
        self.screen.blit(source=font.render(
            self.text, True, pg.color.Color("white")), dest=(self.x, self.y))
