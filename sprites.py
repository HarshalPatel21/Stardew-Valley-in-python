# from typing import Any
import pygame as pg
from settings import *
from settings import LAYERS
from random import randint , choice
from Timer import Timer

class Generic(pg.sprite.Sprite):
    def __init__(self,pos,surf,groups,z = LAYERS['main']) -> None:
        super().__init__(groups)

        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width*0.2,-self.rect.height*0.75)

class Interaction(Generic):
    def __init__(self, pos,size ,groups,name) -> None:
        surf = pg.Surface(size)
        super().__init__(pos, surf, groups)
        self.name = name



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
        self.hitbox = self.rect.copy().inflate(-20,-self.rect.height*0.9)

class Particle(Generic):
    def __init__(self, pos, surf, groups ,z , duration = 200) -> None:
        super().__init__(pos, surf, groups,z)
        self.start_time = pg.time.get_ticks()
        self.duration = duration

    # white surf 
        mask_surf = pg.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface()
        new_surf.set_colorkey((0,0,0))
        self.image = new_surf

    def update(self,dt):
        current_time = pg.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()


class Tree(Generic):
    def __init__(self, pos, surf, groups,name,player_add) -> None:
        super().__init__(pos, surf, groups)

        # tree attributes
        self.health = 5
        self.alive = True
        self.stump_surf = pg.image.load(f'Animations/graphics/stumps/{"small" if name == "Small" else "large"}.png').convert_alpha()
        self.invul_timer = Timer(200)


        #apples 
        self.apple_surf = pg.image.load('Animations/graphics/fruit/apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pg.sprite.Group()
        self.create_fruit()

        self.player_add = player_add


    def damage(self):
        # damage tree 
        self.health -= 1

        # remove apple
        if len(self.apple_sprites.sprites()) > 0:
            
            random_apple = choice(self.apple_sprites.sprites())
            Particle(
                pos =  random_apple.rect.topleft,
                surf= random_apple.image,
                groups= self.groups()[0],
                z = LAYERS['fruit']
            )
            self.player_add('apple')
            random_apple.kill()

    def check_death(self):
        if self.health <= 0:
            Particle(
                pos =  self.rect.topleft,
                surf= self.image,
                groups= self.groups()[0],
                z = LAYERS['fruit'],
                duration= 300
            )
            self.player_add('wood')
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10,-self.rect.height*0.6)
            self.alive = False
    
    def update(self, dt):
        
        if self.alive:
            self.check_death()


    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0,10) < 2 :
                x = pos[0] + self.rect.left 
                y = pos[1] + self.rect.top
                Generic(
                    pos=(x,y),
                    surf= self.apple_surf,
                    groups=[self.apple_sprites,self.groups()[0]],
                    z = LAYERS['fruit']
                    )


