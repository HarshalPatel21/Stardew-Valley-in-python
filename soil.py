import pygame as pg
# from pygame.sprite import _Group
from settings import *
from pytmx.util_pygame import load_pygame 
from support import *

class SoilTile(pg.sprite.Sprite):

    def __init__(self, pos,surf,groups) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']

class SoilLayer:

    def __init__(self,all_sprites) -> None:
        
        # sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pg.sprite.Group()

        # graphics 
        self.soil_surf = pg.image.load('Animations\graphics\soil\o.png')
        self.soil_surfs = import_folder_dict('Animations\graphics\soil')

        self.create_soil_grid()
        self.create_hit_rects()

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
                x = rect.x // TILE_SIZE # converting pixel position to tile positin
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()

    
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
        
    # requirements 

    # if area is farmable 
    # if the soil has been watered
    # if the soil has plant already
