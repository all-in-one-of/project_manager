#!/usr/bin/env python
# coding=utf-8

class LogEntry(object):
    def __init__(self, main, id=0, dependancy="", viewed_by=[], members_concerned=[], created_by="", log_to="", log_type="", log_description="", log_time=""):
        self.main = main
        self.id = id
        self.dependancy = dependancy
        if len(viewed_by) == 0:
            self.viewed_by = ["obolduc", "vdelbroucq", "lclavet", "acorbin", "costiguy", "yshan", "jberger", "lgregoire", "yjobin", "cgonnord", "mroz", "slachapelle", "thoudon", "erodrigue", "mbeaudoin"]
        elif "," in viewed_by:
            self.viewed_by = viewed_by.split(",")
        elif type(viewed_by) == list:
            self.viewed_by = viewed_by
        self.members_concerned = members_concerned
        self.created_by = created_by
        self.log_to = log_to
        self.type = log_type
        self.description = log_description
        self.time = log_time

    def print_log(self):
        print "| -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} | -{} |".format(self.id, self.dependancy, self.viewed_by, self.members_concerned, self.created_by, self.log_to, self.type, self.description, self.time)

    def add_log_to_database(self):
        self.main.cursor.execute('''INSERT INTO log(log_dependancy, viewed_by, members_concerned, created_by, log_to, log_type, log_description, log_time) VALUES(?,?,?,?,?,?,?,?)''', (self.dependancy, ",".join(self.viewed_by), ",".join(self.members_concerned), self.created_by, self.log_to, self.type, self.description, self.time,))
        self.id = self.main.cursor.lastrowid
        self.main.db.commit()

        #self.main.WhatsNew.create_feed_entry(self.main, type=self.type, members_concerned=self.members_concerned, dependancy=self.dependancy, created_by=self.created_by, log_to=self.log_to, description=self.description, log_time=self.time)

    def remove_log_from_database(self):
        self.main.cursor.execute('''DELETE FROM log WHERE log_id=?''', (self.id,))
        self.main.db.commit()

    def update_viewed_by(self):
        self.viewed_by.remove(self.main.username)
        self.main.cursor.execute('''UPDATE log SET viewed_by=? WHERE log_id=?''', (",".join(self.viewed_by), self.id,))
