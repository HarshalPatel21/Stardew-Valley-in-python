import pygame as pg 
from settings import * 
from Timer import Timer

class Menu:
    def __init__(self,player,toggle_menu) -> None:
        
        # general setup
        self.player = player
        self.toggle_menu = toggle_menu

        self.display_surface = pg.display.get_surface()
        self.font = pg.font.Font('Animations/font\LycheeSoda.ttf',30)
        

        # options
        self.width = 400
        self.space = 10
        self.padding = 8 
    
        # entries 
        self.options = list(self.player.item_inventory.keys()) + list(self.player.seed_inventory.keys()) 
        self.sell_order = len(self.player.item_inventory) - 1

        self.setup()

        # movement 
        self.index = 0
        self.timer = Timer(200)

    def display_money(self):
        text_surf = self.font.render(f'${self.player.money}' ,False,'Black')
        text_rect = text_surf.get_rect(midbottom = (SCREEN_WIDTH/2,SCREEN_HEIGHT-20))

        pg.draw.rect(self.display_surface,'White',text_rect.inflate(10,10),0,4)
        self.display_surface.blit(text_surf,text_rect)

    def setup(self):
        
        # create text surfs
        self.text_surfs = []
        self.total_height = 0
        for item in self.options:
            text_surf = self.font.render(item,False,'Black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)

        self.total_height += (len(self.text_surfs) - 1)*self.space
        self.menu_top = SCREEN_HEIGHT/2 - self.total_height/2
        self.main_rect = pg.Rect(SCREEN_WIDTH/2 - self.width/2 ,self.menu_top,self.width,self.total_height)

        # buy / sell text 
        self.buy_text = self.font.render('Buy',False,'Black')
        self.sell_text = self.font.render('Sell',False,'Black')

    def input(self):
        keys = pg.key.get_pressed()
        self.timer.update()

        if keys[pg.K_ESCAPE]:
            self.toggle_menu()
        
        if not self.timer.active:
            if keys[pg.K_UP]:
                self.index -= 1
                self.timer.activate()


            if keys[pg.K_DOWN]:
                self.index += 1
                self.timer.activate()

            if keys[pg.K_SPACE]:
                self.timer.activate()

                # get item 
                curr_item = self.options[self.index]

                # sell 
                if self.index <= self.sell_order:
                    if self.player.item_inventory[curr_item] > 0 :
                        self.player.item_inventory[curr_item] -= 1 
                        self.player.money += SALE_PRICE[curr_item]
                # buy
                else:
                    seed_price = PURCHASE_PRICE[curr_item]
                    if self.player.money >= seed_price:
                        self.player.seed_inventory[curr_item] += 1
                        self.player.money -= seed_price


        # clamp the vals 
        if self.index < 0:
            self.index = len(self.options) - 1

        if self.index > len(self.options)- 1:
            self.index = 0

    
    def show_entry(self,text_surf,amount,top,selected):
        
        # background
        bg_rect =pg.Rect(self.main_rect.left,top,self.width,text_surf.get_height() + self.padding*2)
        pg.draw.rect(self.display_surface,'White',bg_rect,0,4)

        # text 
        text_rect = text_surf.get_rect(midleft = (self.main_rect.left+20,bg_rect.centery))
        self.display_surface.blit(text_surf,text_rect)

        # amount
        amount_surf = self.font.render(str(amount),False,'Black')
        amount_rect = amount_surf.get_rect(midright = (self.main_rect.right -20 ,bg_rect.centery))
        self.display_surface.blit(amount_surf,amount_rect)

        # selected 
        if selected:
            pg.draw.rect(self.display_surface,'Black',bg_rect,4,4)
            if self.index <= self.sell_order : # sell
                pos_rect = self.sell_text.get_rect(midleft = (self.main_rect.left+150,bg_rect.centery))
                self.display_surface.blit(self.sell_text,pos_rect)
            else : # buy
                pos_rect = self.buy_text.get_rect(midleft = (self.main_rect.left+150,bg_rect.centery))
                self.display_surface.blit(self.buy_text,pos_rect)

    def update(self):
        self.input()
        self.display_money()

        for text_index,text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + text_index*(text_surf.get_height() + (self.padding*2) + self.space)
            amount_list = list(self.player.item_inventory.values()) + list(self.player.seed_inventory.values()) 
            amount = amount_list[text_index]
            self.show_entry(text_surf=text_surf,amount=amount,top=top ,selected=self.index == text_index)
        

