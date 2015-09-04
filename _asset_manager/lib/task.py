#!/usr/bin/env python
# coding=utf-8

class Task(object):
    def __init__(self, main, id=0, project_name="", sequence_name="", shot_number="", asset_id="", task_description="", task_department="", task_status="", task_assignation="", task_end="", task_bid="", task_confirmation=0):
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
        self.end = task_end
        self.bid = task_bid
        self.confirmation = task_confirmation

    def print_task(self):
        return "| -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} |".format(self.id, self.project, self.sequence, self.shot, self.asset_id, self.description, self.department, self.status, self.assignation, self.end, self.bid, self.confirmation)

    def add_task_to_db(self):
        self.main.cursor.execute(
            '''INSERT INTO tasks(project_name, sequence_name, shot_number, asset_id, task_description, task_department, task_status, task_assignation, task_end, task_bid, task_confirmation) VALUES(?,?,?,?,?,?,?,?,?,?,?)''',
            (self.project, self.sequence, self.shot, self.asset_id, self.description, self.department, self.status, self.assignation, self.end, self.bid, self.confirmation))
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

    def change_asset_id(self, new_id):
        if self.asset_id == new_id: return
        self.main.cursor.execute('''UPDATE tasks SET asset_id=? WHERE task_id=?''', (new_id, self.id,))
        self.main.db.commit()
        self.asset_id = new_id

    def change_confirmation(self, new_confirmation):
        if self.confirmation == new_confirmation: return
        self.main.cursor.execute('''UPDATE tasks SET task_confirmation=? WHERE task_id=?''', (new_confirmation, self.id,))
        self.main.db.commit()
        self.confirmation = new_confirmation

    def add_comment(self, author, comment, time, type):
        self.main.cursor.execute('''INSERT INTO comments(asset_id, comment_author, comment_text, comment_time, comment_type, comment_image) VALUES(?,?,?,?,?,?)''', (self.id, author, comment, time, type, ""))
        self.main.db.commit()

    def remove_comment(self, author, comment, time):
        self.main.cursor.execute('''DELETE FROM comments WHERE comment_author=? AND comment_text=? AND comment_time=?''', (author, comment, time))
        self.main.db.commit()

    def edit_comment(self, new_comment, comment_author, old_comment, comment_time):
        self.main.cursor.execute('''UPDATE comments SET comment_text=? WHERE comment_author=? AND comment_text=? AND comment_time=?''', (new_comment, comment_author, old_comment, comment_time,))
        self.main.db.commit()

    def get_infos_from_id(self):
        task = self.main.cursor.execute('''SELECT * FROM tasks WHERE task_id=?''', (self.id,)).fetchone()
        project_name = task[1]
        sequence = task[2]
        shot = task[3]
        asset_id = task[4]
        description = task[5]
        department = task[6]
        status = task[7]
        assignation = task[8]
        end = task[9]
        bid = task[10]
        confirmation = task[11]

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
        self.end = end
        self.bid = bid
        self.confirmation = confirmation