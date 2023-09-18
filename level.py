# from typing import Iterable, Union
import pygame as pg
from pygame.sprite import AbstractGroup
from settings import *
from player import Player
from overlay import Overlay
from sprites import *
from pytmx.util_pygame import load_pygame
from support import *
from transition import Transition
from soil import SoilLayer
from sky import Rain
from random import randint


class Level:

    def __init__(self) -> None:
        
        # get display surf
        self.display_surf = pg.display.get_surface()

        # sprite groups
        self.all_sprites = CameraGroup()
        self.collision_sprites = pg.sprite.Group()
        self.tree_sprites = pg.sprite.Group()
        self.interaction_sprites = pg.sprite.Group()


        self.soil_layer = SoilLayer(self.all_sprites,self.collision_sprites)
        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset , self.player)
        
        # sky
        self.rain = Rain(self.all_sprites)
        self.raining = randint(0,10) > 3
        self.soil_layer.raining = self.raining

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
            Generic((x*TILE_SIZE,y*TILE_SIZE),surf,[self.all_sprites,self.collision_sprites])

        # water
        water_frames = import_folder('Animations\graphics\water/')

        for x,y,surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x*TILE_SIZE,y*TILE_SIZE),water_frames,self.all_sprites)

        # Trees
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(
                pos = (obj.x,obj.y),
                surf = obj.image,
                groups = [self.all_sprites,self.collision_sprites , self.tree_sprites],
                name = obj.name,
                player_add = self.player_add
                )

        # wild flowers
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x,obj.y),obj.image,[self.all_sprites,self.collision_sprites])

        # collision tiles
        for x,y,surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x*TILE_SIZE,y*TILE_SIZE),pg.Surface((TILE_SIZE,TILE_SIZE)),self.collision_sprites)


        #Player
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(
                    pos=(obj.x,obj.y),
                    group=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    tree_sprites= self.tree_sprites,
                    interaction = self.interaction_sprites,
                    soil_layer = self.soil_layer
                    )
                
            if obj.name == 'Bed':
                Interaction(
                    pos=(obj.x,obj.y),
                    size=(obj.width,obj.height),
                    groups=self.interaction_sprites,
                    name='Bed'
                )
        
        Generic(
            pos=(0,0),
            surf=pg.image.load('Animations\graphics\world/ground.png').convert_alpha(),
            groups=self.all_sprites,
            z = LAYERS['ground']
        )

    def player_add(self,item):
        self.player.item_inventory[item] += 1

    def reset(self):

        #plants
        self.soil_layer.update_plants()
        
        # soil 
        self.soil_layer.remove_water()

        self.raining = randint(0,10) > 3
        self.soil_layer.raining = self.raining
        if self.raining :
            self.soil_layer.water_all()

        #apples on trees
        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_fruit()

    def run(self,dt):
        self.display_surf.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)

        self.overlay.display()

        # rain 
        if self.raining :
            self.rain.update()

        # transition overlay
        if self.player.sleep:
            self.transition.play()



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

    

