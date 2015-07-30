from PIL import Image
import os
from PyQt4 import QtCore, QtGui
import webbrowser

class Moodboard_Creator():
    def __init__(self, main, image_list):

        self.main = main

        # --------------------------------------------------------------------------
        self.max_image_per_row = 4
        self.vertical_spacing = 18
        self.horizontal_spacing = 18
        self.width_resize = 1500  # Resize horizontal voulu
        self.image_list = []
        self.original_image_list = image_list        #Liste pour l'entierete des images
        for image in self.original_image_list:
            self.image_list.append(Image.open(image))
        self.biggest_image_list = []        #Liste pour les images les plus grandes
        self.max_row = len(self.image_list)     # Le maximum de row est egal a la totalite des item dans la liste
        self.image_canevas = Image.new("RGB", ( 15000, 15000), (12,12,12))  # Creation du canevas (Mode de couleur et grandeur)
        # --------------------------------------------------------------------------

        self.resize_and_drop()

    def resize_and_drop(self):
        self.list_image_numero = 0
        for row in range(self.max_row):     #Pour chaque row dans le maximum donne
            self.first_row_list = []


            if len(self.image_list) < self.max_image_per_row:
                self.max_image_per_row = len(self.image_list)
            else:
                pass

            for first_row_image in range(self.max_image_per_row):            #Trouver les grandeurs de la premiere row
                self.first_row_image_temp = self.image_list[first_row_image]
                wpercent = (self.width_resize / float(self.first_row_image_temp.size[0]))
                hsize = int((float(self.first_row_image_temp.size[1]) * float(wpercent)))
                self.first_row_list.append(hsize)
            if self.list_image_numero < len(self.image_list):


                if row == 0:
                    y_top = self.vertical_spacing
                    y_bottom = max(self.first_row_list) + self.vertical_spacing
                else:
                    y_top = y_bottom + self.vertical_spacing
                    y_bottom = y_top + max(self.max_height_list)

            else:
                pass

            self.max_height_list = []       #Liste des images les plus grandes sur la ligne

            for image in range(self.max_image_per_row):     #Pour chaque image par row dans le maximum donne

                if self.list_image_numero < len(self.image_list):

                    if image == 0:      #si c'est l'image 0 sur la ligne, on retourne a la marge gauche
                        x_left = self.horizontal_spacing
                    else:
                        x_left = x_right + self.horizontal_spacing

                    x_right = x_left + self.width_resize

                    self.image = self.image_list[self.list_image_numero]       #Prendre image selon list_image si existe dans
                    self.list_image_numero = self.list_image_numero + 1         #+1 Pour pouvoir passer a travers les images


                    wpercent = (self.width_resize / float(self.image.size[0]))
                    hsize = int((float(self.image.size[1]) * float(wpercent)))
                    self.resized_image = self.image.resize((self.width_resize, hsize),Image.ANTIALIAS)  # Resize image a resized_image

                    self.max_height_list.append(self.resized_image.size[1])     #Append la hauteur de chaque image a la liste

                    self.image_canevas.paste(self.resized_image, (x_left, y_top))       #Paste image a canevas

                else:          #Si liste_image_numero depasse items dans liste_image
                    pass


            try:
                self.biggest_image_list.append(max(self.max_height_list))
            except ValueError:
                pass

        self.canevas_resize_horizontal = ( ( (self.horizontal_spacing * self.max_image_per_row) + self.horizontal_spacing ) + self.max_image_per_row * self.width_resize )
        self.canevas_resize_vertical = ( (self.vertical_spacing * 4) + sum(self.biggest_image_list) )
        self.cropped_canvas = self.image_canevas.crop((0, 0, self.canevas_resize_horizontal, self.canevas_resize_vertical))     #Canevas Cropped
        fileName = QtGui.QFileDialog.getSaveFileName(self.main, 'Save Moodboard Image', 'H:/', selectedFilter='*.jpg')
        try:
            fileName = os.path.abspath(fileName)
            self.cropped_canvas.save(fileName)
            webbrowser.open(fileName)
        except:
            return





