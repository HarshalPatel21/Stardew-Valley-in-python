import os 
import pygame as pg

def import_folder(path):
    surface_list = []
    for _,__,image_files in os.walk(path):
        
        for image in image_files:
            full_path = path + '/' + image
            image_surf = pg.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list

def import_folder_dict(path):
    surface_dict = {  }
    for _,__,image_files in os.walk(path):
        for image in image_files:
            full_path = path + '/' + image
            image_surf = pg.image.load(full_path).convert_alpha()
            surface_dict[image.split('.')[0]] = image_surf

    return surface_dict
