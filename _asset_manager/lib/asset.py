#!/usr/bin/env python
# coding=utf-8

import os
import time
from datetime import datetime
from datetime import date
import subprocess
from PyQt4 import QtGui, QtCore
from glob import glob

class Asset(object):
    def __init__(self, main, id=0, project_name="", sequence_name="", shot_number="", asset_name="", asset_path="", asset_extension="", asset_type="", asset_version="", asset_tags=[], asset_dependency="", last_access="", last_publish="", creator="", number_of_publishes=0, publish_from_version="", get_infos_from_id=False):

        self.main = main

        if get_infos_from_id == True:
            asset = self.main.cursor.execute('''SELECT * FROM assets WHERE asset_id=?''', (id,)).fetchone()
            project_name = asset[1]
            sequence_name = asset[2]
            shot_number = asset[3]
            asset_name = asset[4]
            asset_extension = asset[6]
            asset_type = asset[7]
            asset_version = asset[8]
            asset_tags = asset[9]
            asset_dependency = asset[10]
            last_access = asset[11]
            last_publish = asset[12]
            creator = asset[13]
            number_of_publishes = asset[14]
            publish_from_version = asset[15]

        self.id = id
        self.project = project_name
        try:
            self.project_shortname = self.main.cursor.execute('''SELECT project_shortname FROM projects WHERE project_name=?''', (self.project,)).fetchone()[0]
        except:
            self.project_shortname = ""
        try:
            self.project_path = self.main.cursor.execute('''SELECT project_path FROM projects WHERE project_name=?''', (self.project,)).fetchone()[0]
        except:
            self.project_path = ""

        if sequence_name == "All":
            sequence_name = "xxx"
        self.sequence = sequence_name
        self.shot = shot_number
        self.name = asset_name
        self.type = asset_type
        self.extension = asset_extension
        self.version = asset_version
        if not asset_tags == None and len(asset_tags) > 0:
            self.tags = asset_tags.split(",")
        else:
            self.tags = []
        self.dependency = asset_dependency
        self.last_access = last_access
        if self.version == "out":
            if last_publish == "" or last_publish == None:
                self.last_publish = self.main.members[self.main.username] + datetime.now().strftime(" on %d/%m/%Y at %H:%M")
                self.last_publish_as_date = date(2010, 01, 01)
            else:
                self.last_publish = last_publish
                last_publish_date = last_publish.split(" ")[2]
                day = last_publish_date.split("/")[0]
                month = last_publish_date.split("/")[1]
                year = last_publish_date.split("/")[2]
                time = last_publish.split(" ")[-1]
                hour = time.split(":")[0]
                minutes = time.split(":")[1]
                self.last_publish_as_date = datetime(int(year), int(month), int(day), int(hour), int(minutes))
        else:
            if last_publish == "" or last_publish == None:
                self.last_publish = self.main.members[self.main.username] + datetime.now().strftime(" on %d/%m/%Y at %H:%M")
                self.last_publish_as_date = date(2010, 01, 01)
            else:
                published_by = last_publish.split(" ")[0]
                if len(published_by) == 0:
                    published_by = self.main.members[self.main.username]

                self.last_publish = last_publish
                last_publish_date = last_publish.split(" ")[2]
                day = last_publish_date.split("/")[0]
                month = last_publish_date.split("/")[1]
                year = last_publish_date.split("/")[2]
                time = last_publish.split(" ")[-1]
                hour = time.split(":")[0]
                minutes = time.split(":")[1]
                self.last_publish_as_date = datetime(int(year), int(month), int(day), int(hour), int(minutes))

        self.number_of_publishes = number_of_publishes
        self.creator = creator
        self.nbr_of_comments = self.main.cursor.execute('''SELECT Count(*) FROM comments WHERE asset_id=? AND comment_type=?''', (self.id, self.type,)).fetchone()[0]
        if self.type == "ref":
            self.path = "\\assets\\{0}\\{1}_{2}_{3}_{0}_{4}_{5}.{6}".format(self.type, self.project_shortname, self.sequence, self.shot, self.name, self.version, self.extension)
        else:
            self.path = "\\assets\\{0}\\{1}_{2}.{3}".format(self.type, self.name, self.version, self.extension)

        if self.type == "cmp":
            self.full_path = asset_path
        else:
            self.full_path = self.project_path + self.path

        # Get the last version of the asset (Ex: if an asset has 5 version, last_version is equal to "05")
        self.last_version = self.main.cursor.execute('''SELECT MAX(asset_version) FROM assets WHERE asset_name=? AND asset_type=? AND asset_version!="out"''', (self.name, self.type,)).fetchone()[0]


        # Default media for asset
        if "-lowres" in self.name:
            self.default_media_manager = self.main.cur_path + "\\media\\default_asset_thumb\\{0}-low.png".format(self.type)
        else:
            self.default_media_manager = self.main.cur_path + "\\media\\default_asset_thumb\\{0}.png".format(self.type)

        # Media generated by the user when publishing an asset.
        # This variable is used for the assetList (for the 1st version of an asset) and for the version list (for any version).
        # If asset is the first version, get the thumbnail of the last version for the asset list.
        # If asset is not the first version, get thumbnail of current version for the version list.

        if self.type in ["anm", "cam"]:
            extension = "png"
        else:
            extension = "jpg"

        if self.version == "01":
            # Variable to use for the version list, to display first version thumbnail instead of the last version's thumbnail (which is used for the assetList)
            self.first_media = self.project_path + "\\assets\\{0}\\.thumb\\{1}_{2}_full.{3}".format(self.type, self.name, self.version, extension)
            self.default_media_user = self.project_path + "\\assets\\{0}\\.thumb\\{1}_{2}_full.{3}".format(self.type, self.name, self.last_version, extension)
        else:
            self.default_media_user = self.project_path + "\\assets\\{0}\\.thumb\\{1}_{2}_full.{3}".format(self.type, self.name, self.version, extension)

        # Create full media variable to use when user press spacebar.
        # If asset is of type mod, tex or rig, it's the same as the default media user
        # If asset is anm, sim, shd or cam, then the full asset is a mp4 video
        if self.type in ["mod", "tex", "shd", "rig"]:
            self.full_media = self.default_media_user
        elif self.type in ["anm", "sim", "cam"]:
            self.full_media = self.project_path + "\\assets\\{0}\\.thumb\\{1}_{2}_full.{3}".format(self.type, self.name, self.version, "mp4")
        else:
            self.full_media = self.project_path + "\\assets\\{0}\\.thumb\\{1}_{2}_full.{3}".format(self.type, self.name, self.version, "mp4")

        # Advanced media displayed when user press on ctrl + spacebar
        self.advanced_media = self.project_path + "\\assets\\{0}\\.thumb\\{1}_{2}_advanced.{3}".format(self.type, self.name, self.version, "mp4")

        self.anim_out_path = self.project_path + "\\assets\\{0}\\{1}_{2}.{3}".format("anm", self.name, "out", "abc")
        self.main_hda_path = self.project_path + "\\assets\\{0}\\{1}_{2}.{3}".format("lay", self.name, "out", "hda")
        self.obj_path = self.project_path + "\\assets\\{0}\\{1}_{2}.{3}".format("mod", self.name, "out", "obj")
        self.rig_out_path = self.project_path + "\\assets\\{0}\\{1}_{2}.{3}".format("rig", self.name, "out", "ma")

        self.comments_folder = self.project_path + "\\assets\\{0}\\.comments".format(self.type)
        self.comment_filename = self.project_path + "\\assets\\{0}\\.comments\\{0}_{1}".format(self.type, self.name)

        self.publish_from_version = publish_from_version

    def print_asset(self):
        print "| -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} |".format(self.id, self.project, self.sequence, self.shot, self.name, self.path, self.type, self.version, self.tags, self.dependency, self.last_access, self.last_publish, self.creator, self.number_of_publishes)

    def update_asset_path(self):
        new_path = "\\assets\\{0}\\{1}_{2}.{3}".format(self.type, self.name, self.version, self.extension)
        if int(self.version) > 1:  # If version is higher than 1, go back to level 1 and increment until there is no existing file with version
            self.change_version_if_asset_already_exists(str(1).zfill(2))
            new_path = "\\assets\\{0}\\{1}_{2}.{3}".format(self.type, self.name, self.version, self.extension)
            while os.path.isfile(self.project_path + new_path): # Increment version until there is no file already existing with same version
                self.change_version_if_asset_already_exists(str(int(self.version) + 1).zfill(2))
                new_path = "\\assets\\{0}\\{1}_{2}.{3}".format(self.type, self.name, self.version, self.extension)

        elif int(self.version) == 1: # If asset is at version 1, increment its version until there is no file already existing with same version
            while os.path.isfile(self.project_path + new_path):
                self.change_version_if_asset_already_exists(str(int(self.version) + 1).zfill(2))
                new_path = "\\assets\\{0}\\{1}_{2}.{3}".format(self.type, self.name, self.version, self.extension)

        os.rename(self.full_path, self.project_path + new_path)
        try:
            os.rename(self.full_path.replace("." + self.extension, "_thumb." + self.extension), self.project_path + new_path.replace("." + self.extension, "_thumb." + self.extension))
        except:
            pass
        self.full_path = self.project_path + new_path
        self.path = new_path
        self.main.cursor.execute('''UPDATE assets SET asset_path=? WHERE asset_id=?''', (new_path, self.id,))
        self.main.db.commit()

    def add_asset_to_db(self):
        while os.path.isfile(self.project_path + self.path):
            if self.version != "out":
                self.change_version_if_asset_already_exists(str(int(self.version) + 1).zfill(2))
                self.path = "\\assets\\{0}\\{1}_{2}.{3}".format(self.type, self.name, self.version, self.extension)
            else:
                break
        self.full_path = self.project_path + self.path
        self.main.cursor.execute('''INSERT INTO assets(project_name, sequence_name, shot_number, asset_name, asset_path, asset_extension, asset_type, asset_version, asset_tags, asset_dependency, last_access, last_publish, creator, number_of_publishes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (self.project, self.sequence, self.shot, self.name, self.path, self.extension, self.type, self.version, ",".join(self.tags), self.dependency, self.last_access, self.last_publish, self.creator, self.number_of_publishes,))
        self.id = self.main.cursor.lastrowid
        self.main.db.commit()

    def remove_asset_from_db(self):
        try:
            os.remove(self.full_path)
        except:
            pass
        try:
            os.remove(self.obj_path)
        except:
            pass
        try:
            os.remove(self.first_media)
        except:
            pass
        try:
            os.remove(self.default_media_user)
        except:
            pass
        try:
            os.remove(self.full_media)
        except:
            pass
        try:
            os.remove(self.advanced_media)
        except:
            pass
        if self.type == "mod":
            try:
                os.remove(self.full_path.replace("\\mod\\", "\\shd\\").replace("_mod_", "_shd_").replace(self.extension, "hda"))
            except:
                pass

            files = glob(self.main.selected_project_path + "\\lay\\*")
            layout_assets_names = {}
            for i in files:
                file_name = os.path.split(i)[-1]
                file_parts = file_name.split("_")
                if len(file_parts) == 6:
                    name = file_parts[4]
                    layout_assets_names[name] = i

            for asset_name, asset_path in layout_assets_names.items():
                if self.name in asset_name:
                    os.remove(asset_path)

        self.main.cursor.execute('''DELETE FROM favorited_assets WHERE asset_id=?''', (self.id,))
        self.main.cursor.execute('''DELETE FROM log WHERE log_dependancy=?''', (self.id,))
        self.main.cursor.execute('''DELETE FROM assets_in_layout WHERE asset_id=?''', (self.id,))
        self.main.cursor.execute('''DELETE FROM uved_assets WHERE asset_id=?''', (self.id,))
        self.main.cursor.execute('''DELETE FROM assets WHERE asset_id=?''', (self.id,))
        self.main.cursor.execute('''DELETE FROM comments WHERE asset_id=?''', (self.id,))
        self.main.cursor.execute('''DELETE FROM tasks WHERE asset_id=?''', (self.id,))
        self.main.cursor.execute('''DELETE FROM publish_comments WHERE asset_id=?''', (self.id,))

        self.main.db.commit()

    def change_version_if_asset_already_exists(self, new_version):
        self.main.cursor.execute('''UPDATE assets SET asset_version=? WHERE asset_id=?''', (new_version, self.id,))
        self.main.db.commit()
        self.version = new_version

    def change_name(self, new_name):
        if self.name == new_name: return
        self.main.cursor.execute('''UPDATE assets SET asset_name=? WHERE asset_id=?''', (new_name, self.id,))
        self.main.db.commit()
        self.name = new_name
        self.update_asset_path()

    def change_sequence(self, new_sequence):
        if self.sequence == new_sequence: return
        self.main.cursor.execute('''UPDATE assets SET sequence_name=? WHERE asset_id=?''', (new_sequence, self.id,))
        self.main.db.commit()
        self.sequence = new_sequence
        self.update_asset_path()

    def change_shot(self, new_shot):
        if self.shot == new_shot: return
        self.main.cursor.execute('''UPDATE assets SET shot_number=? WHERE asset_id=?''', (new_shot, self.id,))
        self.main.db.commit()
        self.shot = new_shot
        self.update_asset_path()

    def change_version(self, new_version):
        if self.version == new_version: return
        self.main.cursor.execute('''UPDATE assets SET asset_version=? WHERE asset_id=?''', (new_version, self.id,))
        self.main.db.commit()
        self.version = new_version
        self.update_asset_path()

    def change_dependency(self, new_dependency):
        self.main.cursor.execute('''UPDATE assets SET asset_dependency=? WHERE asset_id=?''', (new_dependency, self.id,))
        self.main.db.commit()
        self.dependency = new_dependency

    def change_extension(self, new_extension):
        new_path = self.path.replace('.' + self.extension, '.' + new_extension)
        self.main.cursor.execute('''UPDATE assets SET asset_extension=? WHERE asset_id=?''', (new_extension, self.id,))
        self.main.cursor.execute('''UPDATE assets SET asset_path=? WHERE asset_id=?''', (new_path, self.id,))
        self.main.db.commit()
        self.extension = new_extension
        self.path = new_path

    def add_comment(self, author, comment, time, type):
        self.main.cursor.execute('''INSERT INTO comments(asset_id, comment_author, comment_text, comment_time, comment_type, comment_image) VALUES(?,?,?,?,?,?)''', (self.id, author, comment, time, type, ""))
        self.main.db.commit()
        self.nbr_of_comments = self.main.cursor.execute('''SELECT Count(*) FROM comments WHERE asset_id=? AND comment_type=?''', (self.id, self.type,)).fetchone()[0]

    def remove_comment(self, author, comment, time):
        comment_img = self.main.cursor.execute('''SELECT comment_image FROM comments WHERE comment_author=? AND comment_text=? AND comment_time=?''', (author, comment, time)).fetchone()
        self.main.cursor.execute('''DELETE FROM comments WHERE comment_author=? AND comment_text=? AND comment_time=?''', (author, comment, time))
        print(comment_img)
        if comment_img != None:
            os.remove(comment_img)
        self.main.db.commit()
        self.nbr_of_comments = self.main.cursor.execute('''SELECT Count(*) FROM comments WHERE asset_id=? AND comment_type=?''', (self.id, self.type,)).fetchone()[0]

    def edit_comment(self, new_comment, comment_author, old_comment, comment_time):
        self.main.cursor.execute('''UPDATE comments SET comment_text=? WHERE comment_author=? AND comment_text=? AND comment_time=?''', (new_comment, comment_author, old_comment, comment_time,))
        self.main.db.commit()

    def add_tags(self, tags):
        self.tags.extend(tags)
        self.tags = list(set(self.tags))
        self.main.cursor.execute('''UPDATE assets SET asset_tags=? WHERE asset_id=?''', (",".join(self.tags), self.id,))
        self.main.db.commit()

    def remove_tags(self, tags):
        self.tags = list(set(self.tags) - set(tags))
        self.main.cursor.execute('''UPDATE assets SET asset_tags=? WHERE asset_id=?''', (",".join(self.tags), self.id,))
        self.main.db.commit()

    def change_last_access(self):
        last_access = time.strftime(self.main.members[self.main.username] + " on %d/%m/%Y at %H:%M")
        self.last_access = last_access
        self.main.cursor.execute('''UPDATE assets SET last_access=? WHERE asset_id=?''', (last_access, self.id,))
        self.main.db.commit()

    def change_last_publish(self):
        cur_time = datetime.now()
        last_publish = cur_time.strftime(self.main.members[self.main.username] + " on %d/%m/%Y at %H:%M")
        self.last_publish = last_publish
        self.last_publish_as_date = cur_time
        self.number_of_publishes += 1
        self.main.cursor.execute('''UPDATE assets SET last_publish=? WHERE asset_id=?''', (last_publish, self.dependency,))
        if self.type == "mod":
            self.main.cursor.execute('''UPDATE assets SET number_of_publishes=? WHERE asset_id=?''', (self.number_of_publishes, self.dependency,))
        elif self.type == "rig":
            self.main.cursor.execute('''UPDATE assets SET number_of_publishes=? WHERE asset_id=?''', (self.number_of_publishes, self.id,))
        self.main.db.commit()




