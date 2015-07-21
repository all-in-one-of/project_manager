#!/usr/bin/env python
# coding=utf-8

class Task(object):
    def __init__(self, main, id=0, project_name="", sequence_name="", shot_number="", asset_id="", task_description="", task_department="", task_status="", task_assignation="", task_start="", task_end="", task_bid="", task_comments=[], task_confirmation=0):
        self.id = id
        self.main = main
        self.project = project_name
        try:
            self.project_shortname = self.main.cursor.execute('''SELECT project_shortname FROM projects WHERE project_name=?''', (self.project,)).fetchone()[0]
        except:
            self.project_shortname = ""
        self.sequence= sequence_name
        self.shot = shot_number
        self.asset_id = asset_id
        self.description = task_description
        self.department = task_department
        self.status = task_status
        self.assignation = task_assignation
        self.start = task_start
        self.end = task_end
        self.bid = task_bid
        if not task_comments == None and len(task_comments) > 0:
            self.comments = task_comments.split(";")
        else:
            self.comments = []
        self.confirmation = task_confirmation


    def __str__(self):
        return "| -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} |".format(self.id, self.project, self.sequence, self.shot, self.asset_id, self.description, self.department, self.status, self.assignation, self.start, self.end, self.bid, self.comments, task_confirmation)


    def add_task_to_db(self):
        self.main.cursor.execute(
            '''INSERT INTO tasks(project_name, sequence_name, shot_number, asset_id, task_description, task_department, task_status, task_assignation, task_start, task_end, task_bid, task_comment, task_confirmation) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)''',
            (self.project, self.sequence, self.shot, self.asset_id, self.description, self.department, self.status, self.assignation, self.start, self.end, self.bid, ";".join(self.comments), self.confirmation))
        self.id = self.main.cursor.lastrowid
        self.main.db.commit()

    def remove_task_from_db(self):
        self.main.cursor.execute('''DELETE FROM tasks WHERE task_id=?''', (self.id,))
        self.main.db.commit()

    def change_sequence(self, new_sequence):
        if self.sequence == new_sequence: return
        self.main.cursor.execute('''UPDATE tasks SET sequence_name=? WHERE task_id=?''', (new_sequence, self.id,))
        self.main.db.commit()
        self.sequence = new_sequence

    def change_shot(self, new_shot):
        if self.shot == new_shot: return
        self.main.cursor.execute('''UPDATE tasks SET shot_number=? WHERE task_id=?''', (new_shot, self.id,))
        self.main.db.commit()
        self.shot = new_shot

    def change_asset_id(self, new_asset_id):
        if self.asset_id == new_asset_id: return
        self.main.cursor.execute('''UPDATE tasks SET asset_id=? WHERE task_id=?''', (new_asset_id, self.id,))
        self.main.db.commit()
        self.asset_id = new_asset_id


    def change_description(self, new_description):
        if self.description == new_description: return
        self.main.cursor.execute('''UPDATE tasks SET task_description=? WHERE task_id=?''', (new_description, self.id,))
        self.main.db.commit()
        self.description = new_description

    def change_department(self, new_department):
        if self.department == new_department: return
        self.main.cursor.execute('''UPDATE tasks SET task_department=? WHERE task_id=?''', (new_department, self.id,))
        self.main.db.commit()
        self.department = new_department


    def change_status(self, new_status):
        if self.status == new_status: return
        self.main.cursor.execute('''UPDATE tasks SET task_status=? WHERE task_id=?''', (new_status, self.id,))
        self.main.db.commit()
        self.status = new_status


    def change_assignation(self, new_assignation):
        if self.assignation == new_assignation: return
        self.main.cursor.execute('''UPDATE tasks SET task_assignation=? WHERE task_id=?''', (new_assignation, self.id,))
        self.main.db.commit()
        self.assignation = new_assignation

    def change_start(self, new_start):
        if self.start == new_start: return
        self.main.cursor.execute('''UPDATE tasks SET task_start=? WHERE task_id=?''', (new_start, self.id,))
        self.main.db.commit()
        self.start = new_start

    def change_end(self, new_end):
        if self.end == new_end: return
        self.main.cursor.execute('''UPDATE tasks SET task_end=? WHERE task_id=?''', (new_end, self.id,))
        self.main.db.commit()
        self.end = new_end


    def change_bid(self, new_bid):
        if self.bid == new_bid: return
        self.main.cursor.execute('''UPDATE tasks SET task_bid=? WHERE task_id=?''', (new_bid, self.id,))
        self.main.db.commit()
        self.bid = new_bid

    def change_confirmation(self, new_confirmation):
        if self.confirmation == new_confirmation: return
        self.main.cursor.execute('''UPDATE tasks SET task_confirmation=? WHERE task_id=?''', (new_confirmation, self.id,))
        self.main.db.commit()
        self.confirmation = new_confirmation

    def add_comment(self, new_comment):
        if self.comment == new_comment: return
        self.main.cursor.execute('''UPDATE tasks SET task_comment=? WHERE task_id=?''', (new_comment, self.id,))
        self.main.db.commit()
        self.comment = new_comment

    def remove_comment(self, new_comment):
        if self.comment == new_comment: return
        self.main.cursor.execute('''UPDATE tasks SET task_comment=? WHERE task_id=?''', (new_comment, self.id,))
        self.main.db.commit()
        self.comment = new_comment

    def get_task_infos_from_id(self):
        task = self.main.cursor.execute('''SELECT * FROM tasks WHERE task_id=?''', (self.id,)).fetchone()
        project_name = task[1]
        sequence = task[2]
        shot = task[3]
        asset_id = task[4]
        description = task[5]
        department = task[6]
        status = task[7]
        assignation = task[8]
        start = task[9]
        end = task[10]
        bid = task[11]
        comments = task[12]
        confirmation = task[13]

        self.project = project_name
        try:
            self.project_shortname = self.main.cursor.execute('''SELECT project_shortname FROM projects WHERE project_name=?''', (self.project,)).fetchone()[0]
        except:
            self.project_shortname = ""
        self.sequence= sequence
        self.shot = shot
        self.asset_id = asset_id
        self.description = description
        self.department = department
        self.status = status
        self.assignation = assignation
        self.start = start
        self.end = end
        self.bid = bid
        if not comments == None and len(comments) > 0:
            self.comments = comments.split(";")
        else:
            self.comments = []
        self.confirmation = confirmation