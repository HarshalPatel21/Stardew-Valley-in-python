import pygame as pg
from settings import *
from pytmx.util_pygame import load_pygame 
from support import *
from random import choice

class SoilTile(pg.sprite.Sprite):

    def __init__(self, pos,surf,groups) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']

class WaterTile(pg.sprite.Sprite):
    def __init__(self,pos,surf ,groups ) -> None:
        super().__init__(groups)
        self.image = surf 
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil water']

class Plant(pg.sprite.Sprite):
    def __init__(self,plant_type,groups,soil,check_watered) -> None:
        super().__init__(groups)

        # setup
        self.plant_type = plant_type
        self.frames = import_folder(f'Animations\graphics/fruit/{plant_type}')
        self.soil = soil
        self.check_watered =check_watered

        # plant growing
        self.age = 0
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvestable = False

        # sprit setup
        self.image = self.frames[self.age]
        self.y_offset = -16 if plant_type == 'corn' else -8
        self.rect = self.image.get_rect(midbottom = soil.rect.midbottom + pg.math.Vector2(0,self.y_offset))
        self.z = LAYERS['ground plant']

    
    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed

            if int(self.age) > 0:
                self.z = LAYERS['main']
                self.hitbox = self.rect.copy().inflate(-26,-self.rect.height*0.4)

            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True

            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + pg.math.Vector2(0,self.y_offset))


class SoilLayer:

    def __init__(self,all_sprites ,collision_sprites) -> None:
        
        # sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pg.sprite.Group()
        self.water_sprites = pg.sprite.Group()
        self.plant_sprites = pg.sprite.Group()
        self.collision_sprites = collision_sprites

        # graphics 
        self.soil_surfs = import_folder_dict('Animations\graphics\soil')
        self.water_surfs = import_folder('Animations\graphics\soil_water')

        self.create_soil_grid()
        self.create_hit_rects()

        #sounds 
        self.hoe_sound = pg.mixer.Sound('Animations/audio\hoe.wav')
        self.hoe_sound.set_volume(0.05)

        self.plant_sound = pg.mixer.Sound('Animations/audio\plant.wav')
        self.plant_sound.set_volume(0.05)

    def create_soil_grid(self):
        ground = pg.image.load('Animations\graphics\world\ground.png') # since we are not showing it to player we dont need to convert
        h_tiles , v_tiles = ground.get_width() // TILE_SIZE , ground.get_height() // TILE_SIZE

        self.grid = [ [[] for col in range(h_tiles)] for row in range(v_tiles)  ]
        for x,y,_ in load_pygame('Animations/data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')

    def create_hit_rects(self):
        self.hit_rects = []
        for index_row ,row in enumerate(self.grid):
            for index_col ,cell in enumerate(row) :
                if 'F' in cell:
                    x = index_col * TILE_SIZE # converting tile position to pixel positin
                    y = index_row * TILE_SIZE
                    rect = pg.Rect(x,y,TILE_SIZE,TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self,point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                self.hoe_sound.play()
                x = rect.x // TILE_SIZE # converting pixel position to tile positin
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()

                    if self.raining :
                        self.water_all()

    def water(self,target_pos):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                
                # add an entry to the soil grid => 'W'
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
    
                self.grid[y][x].append('W')

                # create water tile
                pos = soil_sprite.rect.topleft
                surf = choice(self.water_surfs)
                WaterTile(pos,surf,[self.all_sprites,self.water_sprites])

    def water_all(self):
        for index_row ,row in enumerate(self.grid):
            for index_col ,cell in enumerate(row) :
                if 'X' in cell and 'W' not in cell:
                    cell.append('W')
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE

                    WaterTile((x,y) , choice(self.water_surfs),[self.all_sprites,self.water_sprites])

    def remove_water(self):

        #destroy all the sprites 
        for sprite in self.water_sprites.sprites():
            sprite.kill()

        # clean up grid
        for row in self.grid:
            for cell in row:
                if 'W' in cell : cell.remove('W')

    def check_watered(self,pos):
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered

    def plant_seed(self,target_pos,seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                self.plant_sound.play()

                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE

                if 'P' not in self.grid[y][x]:
                    self.grid[y][x].append('P')
                    # self.p.seed_inventory[self.selected_seed] -= 1
                    Plant(
                        plant_type= seed,
                        groups = [self.all_sprites , self.plant_sprites, self.collision_sprites],
                        soil= soil_sprite,
                        check_watered=self.check_watered
                    )

    def update_plants(self):
        for plant in self.plant_sprites.sprites():
            plant.grow()

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row ,row in enumerate(self.grid):
            for index_col ,cell in enumerate(row) :
                if 'X' in cell:
                    
                    # tile options
                    t = 'X' in self.grid[index_row-1][index_col]
                    b = 'X' in self.grid[index_row+1][index_col]
                    r = 'X' in row[index_col+1]
                    l = 'X' in row[index_col-1]

                    tile_type = 'o' # basic tile type 

                    # if hell_wall (T-T)

                    # for all sides
                    if all((l , b , r, t)):  tile_type = 'x'

                    # horizontal sides only
                    if l and not any((t,b,r)): tile_type = 'r'
                    if r and not any((t,b,l)): tile_type = 'l'
                    if l and r and not any((t,b)): tile_type = 'lr'

                    # vertical sides only
                    if t and not any((l,r,b)): tile_type = 'b'
                    if b and not any((l,r,t)): tile_type = 't'
                    if t and b and not any((l,r)): tile_type = 'tb'

                    # corners 
                    if l and b and not any((t,r)): tile_type = 'tr'
                    if r and b and not any((t,l)): tile_type = 'tl'
                    if l and t and not any((b,r)): tile_type = 'br'
                    if r and t and not any((b,l)): tile_type = 'bl'

                    # T shapes 
                    if all((t,b,r)) and not l : tile_type = 'tbr'
                    if all((t,b,l)) and not r : tile_type = 'tbl'
                    if all((t,l,r)) and not b : tile_type = 'lrb'
                    if all((l,b,r)) and not t : tile_type = 'lrt'


                    SoilTile(
                        pos = (index_col * TILE_SIZE,index_row * TILE_SIZE), 
                        surf = self.soil_surfs[tile_type],
                        groups = [self.all_sprites,self.soil_sprites]
                        )
        
