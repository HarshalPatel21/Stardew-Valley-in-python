from typing import Iterable, Union
import pygame as pg
from pygame.sprite import AbstractGroup
from settings import *
from player import Player
from overlay import Overlay
from sprites import *
from pytmx.util_pygame import load_pygame
from support import *

class Level:

    def __init__(self) -> None:
        
        # get display surf
        self.display_surf = pg.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self):

        tmx_data = load_pygame('Animations/data/map.tmx')

        # house
        for layer in ['HouseFloor','HouseFurnitureBottom' ]:
            for x,y,surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprites,LAYERS['house bottom'])
        
        
        for layer in ['HouseWalls','HouseFurnitureTop' ]:
            for x,y,surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprites)

        
        # fence
        for x,y,surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x*TILE_SIZE,y*TILE_SIZE),surf,self.all_sprites)

        # water
        water_frames = import_folder('Animations\graphics\water/')

        for x,y,surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x*TILE_SIZE,y*TILE_SIZE),water_frames,self.all_sprites)

        # Trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree((obj.x,obj.y),obj.image,self.all_sprites,obj.name)

        # wild flowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x,obj.y),obj.image,self.all_sprites)



        self.player = Player((640,360),self.all_sprites)
        Generic(
            pos=(0,0),
            surf=pg.image.load('Animations\graphics\world/ground.png').convert_alpha(),
            groups=self.all_sprites,
            z = LAYERS['ground']
        )

    def run(self,dt):
        self.display_surf.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)

        self.overlay.display()


class CameraGroup(pg.sprite.Group):

    def __init__(self) -> None:
        super().__init__()

        self.display_surface = pg.display.get_surface()
        self.offset = pg.math.Vector2()

    def custom_draw(self,player):
        
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT/ 2
        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(),key = lambda sprite : sprite.rect.centery):
                if sprite.z == layer :
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image , offset_rect)

        # for sprite in sorted(self.sprites(), key=lambda sprite: sprite.z * 10000 + sprite.rect.centery):
        #     offset_rect = sprite.rect.copy()  
        #     offset_rect.center -= self.offset  
        #     self.display_surface.blit(sprite.image, offset_rect) 

    
