import pygame as pg
from settings import *
from settings import LAYERS

class Generic(pg.sprite.Sprite):
    def __init__(self,pos,surf,groups,z = LAYERS['main']) -> None:
        super().__init__(groups)

        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z

class Water(Generic):
    def __init__(self, pos, frames, groups) -> None:
        # animation setup 
        self.frame_index = 0
        self.frames = frames
 
        super().__init__(
            pos = pos,
            surf=self.frames[self.frame_index],
            groups = groups,
            z= LAYERS['water']
        )

    def animate(self,dt):
        self.frame_index += 5*dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.image = self.frames[int(self.frame_index)]

    
    def update(self,dt):
        self.animate(dt)

class WildFlower(Generic):

    def __init__(self, pos, surf, groups) -> None:
        super().__init__(pos, surf, groups)

class Tree(Generic):
    def __init__(self, pos, surf, groups,name) -> None:
        super().__init__(pos, surf, groups)



