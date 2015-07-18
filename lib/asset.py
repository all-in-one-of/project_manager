#!/usr/bin/env python
# coding=utf-8

import os

class Asset(object):
    def __init__(self, main, id=0, project_name="", sequence_name="", shot_number="", asset_name="", asset_path="", asset_extension="", asset_type="", asset_version="", asset_comment="", asset_tags=[], asset_dependency="", last_access="", creator=""):
        self.main = main
        self.id = id
        self.project = project_name
        self.project_shortname = self.main.cursor.execute('''SELECT project_shortname FROM projects WHERE project_name=?''', (self.project,)).fetchone()[0]
        self.project_path = self.main.cursor.execute('''SELECT project_path FROM projects WHERE project_name=?''', (self.project,)).fetchone()[0]
        self.sequence = sequence_name
        self.shot = shot_number
        self.name = asset_name
        self.extension = asset_extension
        self.type = asset_type
        self.version = asset_version
        self.comment = asset_comment
        if asset_tags != None: self.tags = asset_tags.split(",")
        else: self.tags = []
        self.dependency = asset_dependency
        self.last_access = last_access
        self.creator = creator
        self.path = "\\assets\\{0}\\{1}_{2}_{3}_{4}_{5}_{6}.{7}".format(self.type, self.project_shortname, self.sequence,
                                                                    self.shot, self.type, self.name, self.version, self.extension)
        self.full_path = self.project_path + self.path


    def __str__(self):
        return "| -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} |".format(self.id, self.project, self.sequence, self.shot, self.name, self.path, self.type, self.version, self.comment, self.tags, self.dependency, self.last_access, self.creator)


    def update_asset_path(self):
        new_path = "\\assets\\{0}\\{1}_{2}_{3}_{4}_{5}_{6}.{7}".format(self.type, self.project_shortname, self.sequence, self.shot, self.type, self.name, self.version, self.extension)
        while os.path.isfile(self.project_path + new_path):
            self.change_version_if_asset_already_exists(str(int(self.version) + 1).zfill(2))
            new_path = "\\assets\\{0}\\{1}_{2}_{3}_{4}_{5}_{6}.{7}".format(self.type, self.project_shortname, self.sequence, self.shot, self.type, self.name, self.version, self.extension)

        os.rename(self.full_path, self.project_path + new_path)
        self.main.cursor.execute('''UPDATE assets SET asset_path=? WHERE asset_id=?''', (new_path, self.id,))
        self.main.db.commit()
        self.full_path = self.project_path + new_path
        self.path = new_path

    def add_asset_to_db(self):
        self.main.cursor.execute('''INSERT INTO assets(project_name, sequence_name, shot_number, asset_name, asset_path, asset_type, asset_version, asset_comment, asset_tags, asset_dependency, last_access, creator) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (self.project, self.sequence, self.shot, self.name, self.path, self.type, self.version, self.comment, ",".join(self.tags), self.dependency, self.last_access, self.creator,))
        self.id = self.main.cursor.lastrowid
        self.main.db.commit()

    def remove_asset_from_db(self):
        self.main.cursor.execute('''DELETE FROM assets WHERE asset_id=?''', (self.id,))
        self.main.db.commit()

    def change_name(self, new_name):
        self.main.cursor.execute('''UPDATE assets SET asset_name=? WHERE asset_id=?''', (new_name, self.id,))
        self.main.db.commit()
        self.name = new_name
        self.update_asset_path()

    def change_sequence(self, new_sequence):
        self.main.cursor.execute('''UPDATE assets SET sequence_name=? WHERE asset_id=?''', (new_sequence, self.id,))
        self.main.db.commit()
        self.sequence = new_sequence
        self.update_asset_path()

    def change_shot(self, new_shot):
        self.main.cursor.execute('''UPDATE assets SET shot_number=? WHERE asset_id=?''', (new_shot, self.id,))
        self.main.db.commit()
        self.shot = new_shot
        self.update_asset_path()

    def change_version(self, new_version):
        self.main.cursor.execute('''UPDATE assets SET asset_version=? WHERE asset_id=?''', (new_version, self.id,))
        self.main.db.commit()
        self.version = new_version
        self.update_asset_path()

    def change_version_if_asset_already_exists(self, new_version):
        self.main.cursor.execute('''UPDATE assets SET asset_version=? WHERE asset_id=?''', (new_version, self.id,))
        self.main.db.commit()
        self.version = new_version

    def add_comment(self, comment):
        self.main.cursor.execute('''UPDATE assets SET asset_name=? WHERE asset_id=?''', (comment, self.id,))
        self.main.db.commit()
        self.version = comment

    def add_tags(self, tags):
        self.tags.extend(tags)
        self.tags = list(set(self.tags))
        self.main.cursor.execute('''UPDATE assets SET asset_tags=? WHERE asset_id=?''', (",".join(self.tags), self.id,))
        self.main.db.commit()

    def remove_tags(self, tags):
        self.tags = list(set(self.tags) - set(tags))
        self.main.cursor.execute('''UPDATE assets SET asset_tags=? WHERE asset_id=?''', (",".join(self.tags), self.id,))
        self.main.db.commit()







