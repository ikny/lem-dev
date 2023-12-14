import pygame as pg
import gui_elements as gui


class AppBar:
    ...


class MixingPult:
    ...


class RecordButton:
    ...


class TrackWiget:
    ...


class Lem:
    def __init__(self) -> None:
        pg.init()
        self.screen = pg.display.set_mode((1280, 720))

        self.clock = pg.time.Clock()
        self.running = True

        self.run()

    def run(self) -> None:
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

                # RENDER YOUR GAME HERE
                gui.Text(self.screen, text="Hello, world!", x=50, y=50).draw()

                # flip() the display to put your work on screen
                pg.display.flip()

        self.clock.tick(30)  # limits FPS to 60

        pg.quit()


if __name__ == "__main__":
    l = Lem()
