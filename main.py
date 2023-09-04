import pygame as pg
import sys
from settings import *
from level import Level

class Game:

    def __init__(self) -> None:
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        pg.display.set_caption('Stardew Valley')
        self.level = Level()
        self.clock = pg.time.Clock()


    def run(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            

            dt = self.clock.tick()/1000
            self.level.run(dt)
            pg.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()