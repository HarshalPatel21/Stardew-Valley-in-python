import pygame as pg
from settings import *
from support import import_folder
from sprites import Generic
from random import randint , choice

class Sky:
    # night time
    def __init__(self) -> None:
        self.display_surface = pg.display.get_surface()
        self.full_surf = pg.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.start_color = [255,255,255]  # day
        self.end_color = (38,101,189)  # night


    def display(self,dt):
        for index , value in enumerate(self.end_color):
            if self.start_color[index] > value:
                self.start_color[index] -= 2*dt 

        self.full_surf.fill(self.start_color)
        self.display_surface.blit(self.full_surf,(0,0),special_flags=pg.BLEND_RGBA_MULT)

class Drop(Generic):
    def __init__(self, surf,pos,moving, groups, z) -> None:
        
        # general
        super().__init__(pos, surf, groups, z)
        self.lifetime = randint(400,500)
        self.start_time = pg.time.get_ticks()

        # moving 
        self.moving = moving
        if self.moving :
            self.pos = pg.math.Vector2(self.rect.topleft)
            self.direction = pg.math.Vector2(-2,4)
            self.speed = randint(200,250)

    def update(self,dt):

        # movement
        if self.moving:
            self.pos += self.direction * self.speed*dt
            self.rect.topleft = (round(self.pos.x) , round(self.pos.y))

        # timer 
        if pg.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

class Rain:
    def __init__(self,all_sprites) -> None:
        self.all_sprites = all_sprites
        self.rain_drops = import_folder('Animations\graphics/rain\drops')
        self.rain_floor = import_folder('Animations\graphics/rain/floor')
        self.floor_w,self.floor_h = pg.image.load('Animations\graphics\world\ground.png').get_size()

    def create_floor(self):
        Drop(
            surf= choice(self.rain_floor),
            pos= (randint(0,self.floor_w),randint(0,self.floor_h)) ,
            moving= False,
            groups= self.all_sprites,
            z= LAYERS['rain floor'],
        )

    def create_drops(self):
        Drop(
            surf= choice(self.rain_drops),
            pos= (randint(0,self.floor_w),randint(0,self.floor_h)) ,
            moving= True,
            groups= self.all_sprites,
            z= LAYERS['rain drops'],
        )

    def update(self):
        self.create_drops()
        self.create_floor()